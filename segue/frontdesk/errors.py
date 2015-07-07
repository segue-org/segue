from segue.errors import SegueError

class TicketIsNotValid(SegueError):
    code = 400
    def to_json(self):
        return { 'message': 'person does not have a valid ticket' }


class CannotPrintBadge(SegueError):
    code = 400
    def to_json(self):
        return { 'message': 'cannot print a badge for this person' }

class MustSpecifyPrinter(SegueError):
    code = 400
    def to_json(self):
        return { 'message': 'you must specify a printer' }

class InvalidPrinter(SegueError):
    code = 400
    def to_json(self):
        return { 'message': 'invalid printer' }

class CannotChangeProduct(SegueError):
    code = 400
    def to_json(self):
        return { 'message': 'this person cannot change products' }

class InvalidPaymentOperation(SegueError):
    code = 400
    def __init__(self, bad_field):
        self.bad_field = bad_field
    def to_json(self):
        return { 'message': '{} must be specified'.format(self.bad_field) }
