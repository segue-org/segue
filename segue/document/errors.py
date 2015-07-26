from segue.errors import SegueError

class DocumentNotFound(SegueError):
    code = 404
    def to_json(self):
        return { 'message': 'could not find document {}'.format(self.args) }

class DocumentGenerationFailed(SegueError):
    code = 500
    def to_json(self):
        return { 'message': 'document could no be generated' }
