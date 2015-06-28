import flask

class ProductBlueprint(flask.Blueprint):
    def __init__(self):
        from controllers import ProductController
        super(ProductBlueprint, self).__init__('products', __name__, url_prefix='/products')
        self.controller = ProductController()
        self.add_url_rule('',                            methods=['GET'],  view_func=self.controller.list)
        self.add_url_rule('/<int:product_id>/purchase',  methods=['POST'], view_func=self.controller.purchase)
        self.add_url_rule('/caravan/<string:hash_code>', methods=['GET'],  view_func=self.controller.caravan_products)
        self.add_url_rule('/proponent',                  methods=['GET'],  view_func=self.controller.proponent_products)
