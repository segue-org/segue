from segue.errors import SegueError

class InvalidCorporate(SegueError):
    code = 400
    def to_json(self):
        return { 'message': 'corporate code is not valid' }

class AccountAlreadyHasCorporate(SegueError):
    code = 400
    def to_json(self):
        return { 'message': 'this account already has a corporate associated to it' }
