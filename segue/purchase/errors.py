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

class NoSuchPurchase(SegueError):
    code = 404
    def to_json(self):
        return { 'message': 'no such purchase' }

class PurchaseIsStale(SegueError):
    code = 404
    def to_json(self):
        return { 'message': 'this purchase is stale and cannot be paid' }

class InvalidPaymentNotification(SegueError):
    code = 400
    def to_json(self):
        return { 'message': 'the notification data from payment provider is not correct for this payment method' }

class InvalidHashCode(SegueError):
    def to_json(self):
        return { 'message': 'invalid hash code: {}'.format(self.args) }

class MustProvideDescription(SegueFieldError):
    FIELD = 'description'
    LABEL = 'object_required'
    MESSAGE = 'please provide promocode description'
