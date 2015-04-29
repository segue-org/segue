import os
import pyPdf
from freezegun import freeze_time
from magic import Magic
from datetime import date, datetime, timedelta
from decimal import Decimal
import mockito
from testfixtures import TempDirectory

from segue.purchase.boleto import BoletoPaymentService
from segue.purchase.boleto.models import BoletoPayment, BoletoTransition
from segue.purchase.boleto.factories import BoletoFactory
from segue.purchase.boleto.parsers import BoletoFileParser

from ..support import SegueApiTestCase, hashie, settings
from ..support.factories import *

class BoletoPaymentServiceTestCases(SegueApiTestCase):
    def setUp(self):
        super(BoletoPaymentServiceTestCases, self).setUp()
        self.boletos  = mockito.Mock()
        self.sequence = mockito.Mock()
        self.hasher   = mockito.Mock()
        self.service  = BoletoPaymentService(boletos=self.boletos, sequence=self.sequence)
        self.hasher = self.service.factory.hasher = mockito.Mock()

    def test_creates_a_payment_on_db(self):
        account = self.create_from_factory(ValidAccountFactory, id=333)
        purchase = self.create_from_factory(ValidPurchaseFactory, id=666, customer=account)
        mockito.when(self.sequence).nextval().thenReturn(5678)
        mockito.when(self.hasher).generate().thenReturn('1111ABCD')

        result = self.service.create(purchase, {})

        self.assertEquals(result.type, 'boleto')
        self.assertEquals(result.__class__, BoletoPayment)
        self.assertEquals(result.status, 'pending')
        self.assertEquals(result.amount, purchase.product.price)
        self.assertEquals(result.due_date, purchase.product.sold_until.date())
        self.assertEquals(result.our_number, 105678)
        self.assertEquals(result.document_hash, '1111ABCD')

    def test_process_a_boleto_into_a_pdf_an_serves_as_a_segue_document(self):
        payment = self.create_from_factory(ValidBoletoPaymentFactory)

        boleto = mockito.Mock()
        mockito.when(self.boletos).create(payment).thenReturn(boleto)
        mockito.when(self.boletos) \
               .as_pdf(boleto, payment.document_hash, settings.STORAGE_DIR) \
               .thenReturn('/tmp/le-pdf-file.pdf')

        result = self.service.process(payment)

        self.assertEquals(
            result['redirectUserTo'], 'http://192.168.33.91:9001/api/documents/le-pdf-file.pdf'
        )

    def test_notify_fully_valid_payment_payment(self):
        payment, purchase, product = self._create_payment()
        payload = self._build_payload(payment)

        transition = self.service.notify(purchase, payment, payload, 'script')

        self.assertEquals(transition.__class__, BoletoTransition)
        self.assertEquals(transition.new_status, 'paid')
        self.assertEquals(transition.errors,  None)

    def test_notify_late_payment(self):
        payment, purchase, product = self._create_payment()
        payload = self._build_payload(payment, payment_date=payment.legal_due_date + timedelta(days=1))

        transition = self.service.notify(purchase, payment, payload, 'script')

        self.assertEquals(transition.new_status, 'pending')
        self.assertEquals(transition.errors,  'late-payment')

    def test_notify_insufficient_payment(self):
        payment, purchase, product = self._create_payment()
        payload = self._build_payload(payment, amount=payment.amount - 10)

        transition = self.service.notify(purchase, payment, payload, 'script')

        self.assertEquals(transition.new_status, 'pending')
        self.assertEquals(transition.errors,  'insufficient-amount')

    def _create_payment(self):
        product  = self.create_from_factory(ValidProductFactory, price=200)
        purchase = self.create_from_factory(ValidPurchaseByPersonFactory, id=444, product=product)
        payment  = self.create_from_factory(ValidBoletoPaymentFactory, id=999, amount=200, purchase=purchase)
        return payment, purchase, product

    def _build_payload(self, payment, **overrides):
        payload = dict(
            our_number   = payment.our_number,
            payment_date = payment.due_date,
            amount       = payment.amount,
            received_at  = datetime.now(),
            line         = 'le-line'
        )
        payload.update(**overrides)
        return payload

class BoletoFactoryTestCases(SegueApiTestCase):
    def setUp(self):
        super(BoletoFactoryTestCases, self).setUp()
        self.factory = BoletoFactory()

    def _build_payment(self):
        product  = self.build_from_factory(ValidProductFactory, price=200)
        purchase = self.build_from_factory(ValidPurchaseByPersonFactory, id=444, product=product)
        payment  = self.build_from_factory(ValidBoletoPaymentFactory, id=999, amount=200, purchase=purchase)
        return payment, purchase, product

    def test_converts_boleto_to_pdf(self):
        payment, purchase, product = self._build_payment()
        boleto = self.factory.create(payment)

        with TempDirectory() as temp_dir:
            self.factory.as_pdf(boleto, 'DEADBABE1234', temp_dir.path)

            # file exists
            temp_dir.check('boleto-DEADBABE1234.pdf')

            # and is a pdf
            filename = temp_dir.getpath('boleto-DEADBABE1234.pdf')
            filetype = Magic().from_file(filename)

            # containing a single page
            self.assertEquals(filetype, 'PDF document, version 1.4')
            pdf = pyPdf.PdfFileReader(open(filename, 'r'))
            self.assertEquals(pdf.getNumPages(), 1)


    def test_boleto_has_correct_routing_data(self):
        payment, purchase, product = self._build_payment()
        result = self.factory.create(payment)

        self.assertEquals(result.carteira, '18')
        self.assertEquals(result.agencia_cedente, "4422")
        self.assertEquals(result.conta_cedente, "00022345")
        self.assertEquals(result.convenio, "1600260")
        self.assertEquals(result.nosso_numero, "0000101234")
        self.assertEquals(result.numero_documento, "16002600000101234")

    def test_boleto_has_correct_dates(self):
        payment, purchase, product = self._build_payment()
        result = self.factory.create(payment)

        self.assertEquals(result.data_vencimento,    payment.due_date)
        self.assertEquals(result.data_documento,     date.today())
        self.assertEquals(result.data_processamento, date.today())

    def test_boleto_has_correct_descriptive_info(self):
        payment, purchase, product = self._build_payment()
        result = self.factory.create(payment)

        self.assertEquals(result.demonstrativo, [
            'produto: ingresso fisl16 - lote 1 - muggles',
            'titular: {}'.format(purchase.customer.name)
        ])
        self.assertEquals(result.sacado, [
            purchase.buyer.name,
            purchase.buyer.complete_address,
            purchase.buyer.document
        ])

        self.assertEquals(result.cedente_documento, "01.222.682/0001-01")
        self.assertEquals(result.cedente_endereco, "Rua Rufi\xc3\xa3o Moura, 1234, cj 99 - Floresta - 90.920-008 - Porto Alegre/RS")
        self.assertEquals(result.cedente, "Empresa Organizadora de Eventos Ltda")

    def test_boletos_due_on_weekend_tolerate_next_biz_day_payment(self):
        friday   = date(2015,04,24)
        saturday = date(2015,04,25)
        sunday   = date(2015,04,26)
        monday   = date(2015,04,27)

        payment1 = self.build_from_factory(ValidBoletoPaymentFactory, due_date=friday)
        payment2 = self.build_from_factory(ValidBoletoPaymentFactory, due_date=saturday)
        payment3 = self.build_from_factory(ValidBoletoPaymentFactory, due_date=sunday)
        payment4 = self.build_from_factory(ValidBoletoPaymentFactory, due_date=monday)

        self.assertEquals(payment1.legal_due_date, friday)
        self.assertEquals(payment2.legal_due_date, monday)
        self.assertEquals(payment3.legal_due_date, monday)
        self.assertEquals(payment4.legal_due_date, monday)



class BoletoFileParserTestCases(SegueApiTestCase):
    def setUp(self):
        super(BoletoFileParserTestCases, self).setUp()
        self.parser = BoletoFileParser()

    def _load_file(self, filename):
        path = os.path.join(os.path.dirname(__file__), 'fixtures', filename)
        return open(path,'r').read()


    @freeze_time("2015-03-26 07:33:55")
    def test_parses_one_boleto_return_for_each_line(self):
        content = self._load_file('boletos.bbt')

        result = self.parser.parse(content)

        self.assertEquals(len(result), 10)

        self.assertEquals(result[0]['our_number'],   100561)
        self.assertEquals(result[0]['payment_date'], date(2015,03,25))
        self.assertEquals(result[0]['amount'],       Decimal(60))
        self.assertEquals(result[0]['line'],         '04422;000000022345;18;027;00016002600001005616;            ;                                   ;00000000;25032015;LQB;00000000006000;0000000005856;*; 0000000000; 0000000144; 0000000000;01981')
        self.assertEquals(result[0]['received_at'],  datetime(2015,3,26,7,33,55))
