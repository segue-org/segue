from segue.errors import SegueError

class NotificationExpired(SegueError):
    code = 400
    def to_json(self):
        return { 'message': 'This notification has already expired and is no longer valid' }

class NotificationAlreadyAnswered(SegueError):
    code = 400
    def to_json(self):
        return { 'message': 'This notification has already been answered' }

class NoSuchNotification(SegueError):
    code = 404
    def to_json(self):
        return { 'message': 'no such notification' }

class NoSuchSlot(SegueError):
    code = 404
    def to_json(self):
        return { 'message': 'no such slot' }

class SlotIsEmpty(SegueError):
    code = 400
    def to_json(self):
        return { 'message': 'slot is not empty' }

class SlotNotDirty(SegueError):
    code = 400
    def to_json(self):
        return { 'message': 'slot is not dirty' }



