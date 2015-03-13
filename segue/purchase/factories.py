from segue.factory import Factory

from models import Buyer, Purchase, Payment, PagSeguroPayment

class BuyerFactory(Factory):
    model = Buyer

class PurchaseFactory(Factory):
    model = Purchase

    @classmethod
    def create(cls, buyer, product, account):
        result = cls.model()
        result.buyer = buyer
        result.product = product
        result.customer = account
        return result

class PaymentFactory(Factory):
    model = Payment

class PagSeguroPaymentFactory(Factory):
    model = PagSeguroPayment

    @classmethod
    def create(cls, purchase, other_valid_payments=[]):
        outstanding = purchase.product.price
        for payment in other_valid_payments:
            outstanding -= payment.amount

        reference = "A{0:05d}-PU{1:05d}".format(purchase.customer.id, purchase.id)

        return PagSeguroPayment(purchase=purchase, amount=outstanding, reference=reference)
