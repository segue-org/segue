import flask

from controllers import *
from responses import *

class FrontdeskReceptionBlueprint(flask.Blueprint):
    def __init__(self):
        super(FrontdeskReceptionBlueprint, self).__init__('fd.reception', __name__, url_prefix='/fd/reception')
        self.controller = ReceptionController()

        self.add_url_rule('/<string:hash_code>', methods=['GET'], view_func=self.controller.get_by_hash)

class FrontdeskPersonBlueprint(flask.Blueprint):
    def __init__(self):
        super(FrontdeskPersonBlueprint, self).__init__('fd.person', __name__, url_prefix='/fd/people')
        self.controller = PersonController()
        self.add_url_rule('',                          methods=['GET'],   view_func=self.controller.list)
        self.add_url_rule('',                          methods=['POST'],  view_func=self.controller.create)
        self.add_url_rule('/<int:person_id>',          methods=['GET'],   view_func=self.controller.get_one)
        self.add_url_rule('/<int:person_id>',          methods=['PATCH'], view_func=self.controller.patch)

        self.add_url_rule('/<int:person_id>/buyer',    methods=['GET'],   view_func=self.controller.buyer)
        self.add_url_rule('/<int:person_id>/related',  methods=['GET'],   view_func=self.controller.related)
        self.add_url_rule('/<int:person_id>/eligible', methods=['GET'],   view_func=self.controller.eligible)

        self.add_url_rule('/<int:person_id>/product',  methods=['POST'],  view_func=self.controller.set_product)
        self.add_url_rule('/<int:person_id>/promo',    methods=['POST'],  view_func=self.controller.apply_promo)
        self.add_url_rule('/<int:person_id>/pay',      methods=['POST'],  view_func=self.controller.make_payment)
        self.add_url_rule('/<int:person_id>/badge',    methods=['GET'],   view_func=self.controller.get_badge)
        self.add_url_rule('/<int:person_id>/badge',    methods=['POST'],  view_func=self.controller.create_badge)

class FrontdeskBadgeBlueprint(flask.Blueprint):
    def __init__(self):
        super(FrontdeskBadgeBlueprint, self).__init__('fd.badge', __name__, url_prefix='/fd/badges')
        self.controller = BadgeController()
        self.add_url_rule('/<int:badge_id>/give',  methods=['POST'], view_func=self.controller.give)

class PrinterBlueprint(flask.Blueprint):
    def __init__(self):
        super(PrinterBlueprint, self).__init__('fd.printers', __name__, url_prefix='/fd/printers')
        self.controller = PrinterController()
        self.add_url_rule('',  methods=['GET'], view_func=self.controller.list)

class VisitorBlueprint(flask.Blueprint):
    def __init__(self):
        super(VisitorBlueprint, self).__init__('fd.visitor', __name__, url_prefix='/fd/visitors')
        self.controller = VisitorController()
        self.add_url_rule('', methods=['POST'], view_func=self.controller.create)

class ReportBlueprint(flask.Blueprint):
    def __init__(self):
        super(ReportBlueprint, self).__init__('fd.report', __name__, url_prefix='/fd/reports')
        self.controller = ReportController()
        self.add_url_rule('',               methods=['GET'], view_func=self.controller.get_report)
        self.add_url_rule('/<string:date>', methods=['GET'], view_func=self.controller.get_report)


def load_blueprints():
    return [
        FrontdeskReceptionBlueprint(),
        FrontdeskBadgeBlueprint(),
        FrontdeskPersonBlueprint(),
        ReportBlueprint(),

        PrinterBlueprint(),
        VisitorBlueprint(),
    ]
