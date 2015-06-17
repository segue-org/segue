from segue.responses import BaseResponse

class ProposalInviteResponse(BaseResponse):
    def __init__(self, invite, links=False):
        super(ProposalInviteResponse, self).__init__()
        self.id         = invite.id
        self.account_id = invite.account.id if invite.account else None
        self.name       = invite.name
        self.email      = invite.recipient
        self.status     = invite.status

class TournamentShortResponse(BaseResponse):
    def __init__(self, tournament, links=False):
        super(TournamentShortResponse, self).__init__()
        self.id        = tournament.id
        self.selection = tournament.selection
        self.status    = tournament.status
        self.round     = tournament.current_round

class TournamentDetailResponse(TournamentShortResponse):
    def __init__(self, tournament, links=False):
        super(TournamentDetailResponse, self).__init__(tournament)
        self.rounds = [ tournament.status_of_round(i) for i in range(1, tournament.current_round+1) ]

class StandingsResponse(BaseResponse):
    def __init__(self, player, links=False):
        super(StandingsResponse, self).__init__()
        self.id        = player.proposal.id
        self.title     = player.proposal.title
        self.points    = player.points
        self.victories = player.victories
        self.ties      = player.ties
        self.defeats   = player.defeats
        self.author    = player.proposal.owner.name
        self.position  = player.position
        if player.proposal.track:
            self.zone      = player.proposal.track.name_pt.split(" - ")[0]
            self.area      = player.proposal.track.name_pt.split(" - ")[1]

class RankingResponse(BaseResponse):
    def __init__(self, ranked, links=False):
        super(RankingResponse, self).__init__()
        self.id        = ranked.proposal.id
        self.title     = ranked.proposal.title
        self.author    = ranked.proposal.owner.name
        self.tags      = ranked.tag_names
        self.ranking   = ranked.rank
        if ranked.proposal.track:
            self.zone      = ranked.proposal.track.name_pt.split(" - ")[0]

class AccountShortResponse(BaseResponse):
    def __init__(self, account, links=False):
        super(AccountShortResponse, self).__init__()
        self.id           = account.id
        self.name         = account.name
        self.email        = account.email

        self.has_valid_purchases = account.has_valid_purchases

class AccountDetailResponse(BaseResponse):
    def __init__(self, account, links=True):
        super(AccountDetailResponse, self).__init__()
        self.id           = account.id
        self.name         = account.name
        self.email        = account.email
        self.role         = account.role
        self.document     = account.document
        self.country      = account.country
        self.state        = account.state
        self.city         = account.city
        self.phone        = account.phone
        self.organization = account.organization
        self.created      = account.created
        self.last_updated = account.last_updated
        self.resume       = account.resume

        self.has_valid_purchases = account.has_valid_purchases

        if links:
            self.add_link('proposals', account.proposals,     'admin.list_proposals', owner_id   =account.id)
            self.add_link('purchases', account.purchases,     'admin.list_purchases', customer_id=account.id)
            self.add_link('payments',  account.payments,      'admin.list_payments',  customer_id=account.id)
            self.add_link('caravans',  account.caravan_owned, 'admin.list_caravans',  owner_id   =account.id)

class TrackDetailResponse(BaseResponse):
    def __init__(self, track, links=False):
        self.id      = track.id
        self.name_pt = track.name_pt
        self.name_en = track.name_en
        self.public  = track.public
        self.zone    = track.name_pt.split(" - ")[0]
        self.track   = track.name_pt.split(" - ")[1]

class ProposalDetailResponse(BaseResponse):
    def __init__(self, proposal, links=True):
        self.id           = proposal.id
        self.title        = proposal.title
        self.full         = proposal.full
        self.level        = proposal.level
        self.language     = proposal.language
        self.created      = proposal.created
        self.last_updated = proposal.last_updated
        self.tags         = proposal.tag_names
        self.track     = TrackDetailResponse.create(proposal.track, links=False)

        self.coauthors = ProposalInviteResponse.create(proposal.coauthors.all(), links=False)
        self.owner     = AccountShortResponse.create(proposal.owner, links=False)


        if links:
            self.add_link('invites', proposal.invites.all(), 'admin.list_proposal_invites', proposal_id=proposal.id)
            self.add_link('owner',   proposal.owner,         'admin.get_account',           account_id =proposal.owner.id)

class PurchaseDetailResponse(BaseResponse):
    def __init__(self, purchase, links=True):
        self.id             = purchase.id
        self.product_id     = purchase.product_id
        self.customer_id    = purchase.customer_id
        self.buyer_id       = purchase.buyer_id
        self.status         = purchase.status
        self.created        = purchase.created
        self.last_updated   = purchase.last_updated
        self.kind           = purchase.kind

        self.buyer   = BuyerDetailResponse.create(purchase.buyer)
        self.product = ProductDetailResponse.create(purchase.product)

        if links:
            self.add_link('payments', purchase.payments.all(), 'admin.list_payments', purchase_id = purchase.id)
            self.add_link('customer', purchase.customer,       'admin.get_account',   account_id  = purchase.customer.id)

class ProductDetailResponse(BaseResponse):
    def __init__(self, product, links=True):
        self.id          = product.id
        self.kind        = product.kind
        self.category    = product.category
        self.public      = product.public
        self.price       = product.price
        self.sold_until  = product.sold_until
        self.description = product.description

class BuyerDetailResponse(BaseResponse):
    def __init__(self, buyer, links=True):
        self.id              = buyer.id
        self.kind            = buyer.kind
        self.name            = buyer.name
        self.document        = buyer.document
        self.contact         = buyer.contact
        self.address_street  = buyer.address_street
        self.address_number  = buyer.address_number
        self.address_extra   = buyer.address_extra
        self.address_zipcode = buyer.address_zipcode
        self.address_city    = buyer.address_city
        self.address_country = buyer.address_country

class PaymentDetailResponse(BaseResponse):
    def __init__(self, payment, links=True):
        self.__dict__    = payment.to_json();
        self.transitions = TransitionDetailResponse.create(payment.transitions.all())

class TransitionDetailResponse(BaseResponse):
    def __init__(self, transition, links=True):
        self.__dict__ = transition.to_json()
