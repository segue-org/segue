from segue.errors import SegueError

class InvalidCaravan(SegueError):
    code = 400
    def to_json(self):
        return { 'message': 'caravan code is not valid' }

class AccountAlreadyHasCaravan(SegueError):
    code = 400
    def to_json(self):
        return { 'message': 'this account already has a caravan' }


