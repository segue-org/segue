from segue.errors import SegueError

class CertificateCannotBeIssued(SegueError):
    code = 400
    def to_json(self, *args):
        return { 'message' : 'this certificate cannot be issued for this account' }
