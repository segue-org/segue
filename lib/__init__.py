import flask

import api

class Application(flask.Flask):
    def __init__(self):
        super(Application, self).__init__(__name__)
        self.debug = True

        for blueprint in api.blueprints:
            self.register_blueprint(blueprint)
