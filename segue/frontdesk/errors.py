from segue.errors import SegueError

class TicketIsNotValid(SegueError):
    code = 400

    def to_json(self):
        return { 'message': 'person does not have a valid ticket' }


class CannotPrintBadge(SegueError):
    code = 400

    def to_json(self):
        return { 'message': 'cannot print a badge for this person' }
