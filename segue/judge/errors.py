from segue.errors import SegueError

class NoMatchAvailable(SegueError):
    code = 400
    def to_json(self):
        return { 'message': 'There is no match available for this hash' }

class InvalidJudge(SegueError):
    code = 400
    def to_json(self):
        return { 'message': 'This hash code is not valid' }

class JudgeAlreadyExists(SegueError):
    code = 400
    def to_json(self):
        return { 'message': 'Judge already exists for this e-mail in this tournament' }

class NoSuchTournament(SegueError):
    code = 400
    def to_json(self):
        return { 'message': 'No such tournament' }

class MatchAlreadyJudged(SegueError):
    code = 400
    def to_json(self):
        return { 'message': 'This match has already been judged, and cannot be judged again' }

class MatchAssignedToOtherJudge(SegueError):
    code = 400
    def to_json(self):
        return { 'message': 'This match has been assigned to other judge' }


