from segue.errors import SegueError

class DocumentNotFound(SegueError):
    code = 404
    def to_json(self):
        return { 'message': 'could not find document {}'.format(self.args) }
