import pyPdf
from magic import Magic
from datetime import date
import mockito
from testfixtures import TempDirectory

from segue.purchase.boleto import BoletoPaymentService
from segue.purchase.boleto.models import BoletoPayment
from segue.purchase.boleto.factories import BoletoFactory

from ..support import SegueApiTestCase, hashie
from ..support.factories import *

class BoletoPaymentServiceTestCases(SegueApiTestCase):
    def setUp(self):
        super(BoletoPaymentServiceTestCases, self).setUp()
        self.boletos  = mockito.Mock()
        self.sequence = mockito.Mock()
        self.service  = BoletoPaymentService(boletos=self.boletos, sequence=self.sequence)

    def test_creates_a_payment_on_db(self):
        account = self.create_from_factory(ValidAccountFactory, id=333)
        purchase = self.create_from_factory(ValidPurchaseFactory, id=666, customer=account)
        mockito.when(self.sequence).nextval().thenReturn(5678)

        result = self.service.create(purchase, {})

        self.assertEquals(result.type, 'boleto')
        self.assertEquals(result.__class__, BoletoPayment)
        self.assertEquals(result.status, 'pending')
        self.assertEquals(result.amount, purchase.product.price)
        self.assertEquals(result.due_date, purchase.product.sold_until.date())
        self.assertEquals(result.our_number, 105678)

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
            purchase.buyer.complete_address
        ])

        self.assertEquals(result.cedente_documento, "01.222.682/0001-01")
        self.assertEquals(result.cedente_endereco, "Rua Rufi\xc3\xa3o Moura, 1234, cj 99 - Floresta - 90.920-008 - Porto Alegre/RS")
        self.assertEquals(result.cedente, "Empresa Organizadora de Eventos Ltda")
