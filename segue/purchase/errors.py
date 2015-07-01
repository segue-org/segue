from segue.errors import SegueError, SegueFieldError

class PaymentVerificationFailed(SegueError):
    code = 500
    def to_json(self):
        return { 'message': 'the fetching notification data from payment provider failed' }

class PurchaseAlreadySatisfied(SegueError):
    code = 400;
    def to_json(self):
        return { 'message': 'this purchase has already been paid completely' }

class NoSuchPayment(SegueError):
    code = 404
    def to_json(self):
        return { 'message': 'notification was sent to an invalid payment' }

class InvalidPaymentNotification(SegueError):
    code = 400
    def to_json(self):
        return { 'message': 'the notification data from payment provider is not correct for this payment method' }

class MustProvideDescription(SegueFieldError):
    FIELD = 'description'
    LABEL = 'object_required'
    MESSAGE = 'please provide promocode description'

