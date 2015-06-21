from segue.errors import SegueError, SegueFieldError, NotAuthorized

class InvalidResetPassword(SegueError):
    code = 400
    def to_json(self):
        return { 'message': 'invalid reset password code' }

class NoSuchAccount(SegueError):
    code = 404
    def to_json(self):
        return { 'message': 'no such account' }

class InvalidLogin(SegueError):
    code = 400
    def to_json(self):
        return { 'message': 'bad login' }

class EmailAlreadyInUse(SegueFieldError):
    code = 422

    FIELD = 'email'
    LABEL = 'already_in_use'
    MESSAGE = 'this e-mail address is already registered'

    def __init__(self, email):
        super(EmailAlreadyInUse, self).__init__()
        self.value = email

    def to_json(self):
        return [ self.__dict__ ]



