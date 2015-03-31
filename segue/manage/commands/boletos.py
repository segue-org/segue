from segue.purchase import PaymentService
from segue.purchase.boleto import BoletoPaymentService
from segue.purchase.boleto.parsers  import BoletoFileParser

from colorama import init, Fore as F, Back as B
init()
LINE = "\n"

def process_boletos(filename):
    content = open(filename, 'r').read()

    boleto_service = BoletoPaymentService()
    payment_service = PaymentService()
    parser = BoletoFileParser()

    for entry in parser.parse(content):
        print F.RESET  + LINE
        print F.YELLOW + entry['line']

        payment = boleto_service.get_by_our_number(entry.pop('our_number'))

        if not payment:
            print F.RED + "**** COULD NOT FIND PAYMENT FOR LINE: {line}".format(**entry)
            continue

        print F.RESET + "**** FOUND PAYMENT, applying transition"

        purchase, transition = payment_service.notify(payment.purchase.id, payment.id, entry, 'script')

        print F.YELLOW + "id={0.id} {0.old_status}->{0.new_status}\tR$ {0.paid_amount} ".format(transition)

        if transition.errors:
            print F.RED + "**** BAD TRANSITION! errors were: {0.errors}".format(transition)
            continue;
        else:
            print F.GREEN + "**** GOOD TRANSITION!"
            continue


