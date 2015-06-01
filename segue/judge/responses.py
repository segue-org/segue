from segue.responses import BaseResponse

class JudgeResponse(BaseResponse):
    def __init__(self, judge, links=False):
        super(JudgeResponse, self).__init__()
        self.id        = judge.id
        self.hash      = judge.hash
        self.votes     = judge.votes
        self.email     = judge.email
        self.spent     = judge.spent
        self.remaining = judge.remaining

class AuthorResponse(BaseResponse):
    def __init__(self, account, links=False):
        super(AuthorResponse, self).__init__()
        self.name = account.name
        self.resume = account.resume

class CoauthorResponse(BaseResponse):
    def __init__(self, proposal_invite, links=False):
        super(AuthorResponse, self).__init__()
        self.name   = proposal_invite.account.name
        self.resume = proposal_invite.account.resume

class PlayerResponse(BaseResponse):
    def __init__(self, proposal, links=False):
        super(PlayerResponse, self).__init__()
        self.id           = proposal.id
        self.title        = proposal.title
        self.full         = proposal.full
        self.level        = proposal.level
        self.language     = proposal.language

        self.track     = TrackDetailResponse.create(proposal.track, links=False)
        self.authors   = []
        self.authors.append(AuthorResponse.create(proposal.owner))
        for coauthor in proposal.coauthors.all():
            self.authors.append(AuthorResponse.create(coauthor.account))

class TrackDetailResponse(BaseResponse):
    def __init__(self, track, links=False):
        self.id      = track.id
        self.name_pt = track.name_pt
        self.name_en = track.name_en
        self.public  = track.public
        self.zone    = track.name_pt.split(" - ")[0]
        self.track   = track.name_pt.split(" - ")[1]

class MatchResponse(BaseResponse):
    def __init__(self, match, links=False):
        super(MatchResponse, self).__init__()
        self.id      = match.id
        self.player1 = PlayerResponse.create(match.player1)
        self.player2 = PlayerResponse.create(match.player2)


