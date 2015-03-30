from segue.purchase import PaymentService
from segue.purchase.boleto import BoletoPaymentService
from segue.purchase.boleto.parsers  import BoletoFileParser

def process_boletos(filename):
    content = open(filename, 'r').read()
    boleto_service = BoletoService()
    payment_service = PaymentService()

    parser = BoletoParser()
    for entry in parser.parse(filename):
        payment = boleto_service.get_by_our_number(entry.pop('our_number'))

        if not payment:
            print "**** COULD NOT FIND PAYMENT FOR LINE: {0.line}".format(entry)
            continue

        print "**** FOUND PAYMENT ****"

        transition = payment_service.notify(payment.purchase.id, payment.id, entry, 'script')

        if transition.errors:
            print "**** BAD TRANSITION! errors were: {0.errors}".format(transition)
            continue;

        if transition.is_payment:
            print "******** NOTIFYING CUSTOMER! *******"
            continue



