import os.path
from datetime import date

from pyboleto.bank.bancodobrasil import BoletoBB
from pyboleto.pdf import BoletoPDF

from segue.factory import Factory
from segue.core import config
from ..factories import PaymentFactory

from models import BoletoPayment

class BoletoPaymentFactory(Factory):
    model = BoletoPayment

    @classmethod
    def create(cls, purchase, payment_id):
        payment = PaymentFactory.create(purchase, target_model=cls.model)
        payment.due_date = purchase.product.sold_until.date()
        payment.our_number = "{:010d}".format(config.BOLETO_OFFSET + payment_id)
        payment.document_hash = ""
        return payment


class BoletoFactory(object):
    def __init__(self):
        pass

    def as_pdf(self, boleto_data, document_hash, dest_dir):
        filename = "boleto-{}.pdf".format(document_hash)
        path = os.path.join(dest_dir, filename)

        pdf = BoletoPDF(path)
        pdf.drawBoleto(boleto_data)
        pdf.save()
        return path

    def create(self, payment):
        boleto = BoletoBB(config.BOLETO_TIPO_CONVENIO, None)

        boleto.nosso_numero      = payment.our_number
        boleto.convenio          = config.BOLETO_CONVENIO
        boleto.numero_documento  = "{}{}".format(boleto.convenio, boleto.nosso_numero)
        boleto.especie_documento = 'DM'

        boleto.carteira          = config.BOLETO_CARTEIRA
        boleto.agencia_cedente   = config.BOLETO_AGENCIA
        boleto.conta_cedente     = config.BOLETO_CONTA # TODO: what about digito-verificador?
        boleto.cedente_documento = config.BOLETO_CNPJ
        boleto.cedente_endereco  = config.BOLETO_ENDERECO
        boleto.cedente           = config.BOLETO_EMPRESA

        boleto.data_vencimento    = payment.due_date
        boleto.data_documento     = date.today()
        boleto.data_processamento = date.today()

        boleto.instrucoes    = self._build_instructions()
        boleto.demonstrativo = self._build_description(payment)
        boleto.sacado        = self._build_sacado(payment)

        boleto.valor_documento = payment.amount
        return boleto

    def _build_description(self, payment):
        return [
            "produto: {}".format(payment.purchase.description),
            "titular: {}".format(payment.purchase.customer.name)
        ]

    def _build_sacado(self, payment):
        return [
            payment.purchase.buyer.name,
            payment.purchase.buyer.complete_address
        ]

    def _build_instructions(self):
        return [
            "****NAO RECEBER APOS VENCIMENTO******",
            "NAO UTILIZE PAGAMENTO VIA DOC, DEPOSITO OU TRANSFERENCIA."
        ]
