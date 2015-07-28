from segue.responses import BaseResponse

class AccountResponse(BaseResponse):
    def __init__(self, account):
        self.id = account.id
        self.name              = account.name
        self.city              = account.city
        self.role              = account.role
        self.phone             = account.phone
        self.email             = account.email
        self.resume            = account.resume
        self.country           = account.country
        self.created           = account.created
        self.document          = account.document
        self.badge_name        = account.badge_name
        self.last_updated      = account.last_updated
        self.organization      = account.organization
        self.certificate_name  = account.certificate_name

        self.has_filled_survey = account.survey_answers.count() > 0
