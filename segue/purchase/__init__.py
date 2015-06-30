import flask

from controllers import PurchaseController, PaymentController

class PurchaseBlueprint(flask.Blueprint):
    def __init__(self):
        super(PurchaseBlueprint, self).__init__('purchases', __name__, url_prefix='/purchases')
        self.controller = PurchaseController()
        self.add_url_rule('',                                       methods=['GET'],  view_func=self.controller.list)
        self.add_url_rule('/mode',                                  methods=['GET'],  view_func=self.controller.current_mode)
        self.add_url_rule('/<string:name>.schema',                  methods=['GET'],  view_func=self.controller.schema)
        self.add_url_rule('/<int:purchase_id>',                     methods=['GET'],  view_func=self.controller.get_one)
        self.add_url_rule('/<int:purchase_id>/pay/<string:method>', methods=['POST'], view_func=self.controller.pay)
        self.add_url_rule('/<int:purchase_id>/clone',               methods=['POST'], view_func=self.controller.clone)
        self.add_url_rule('/promocode/<string:hash>',               methods=['GET'],  view_func=self.controller.check_promocode)

class PaymentBlueprint(flask.Blueprint):
    def __init__(self):
        super(PaymentBlueprint, self).__init__('purchase_payments', __name__, url_prefix='/purchases/<int:purchase_id>/payments')
        self.controller = PaymentController()
        self.add_url_rule('/<int:payment_id>/guide',    methods=['GET'],  view_func=self.controller.guide)
        self.add_url_rule('/<int:payment_id>/notify',   methods=['POST'], view_func=self.controller.notify)
        self.add_url_rule('/<int:payment_id>/conclude', methods=['GET'],  view_func=self.controller.conclude)
