from ..core import jwt
from flask import request, current_app
from werkzeug.local import LocalProxy
from models import TokenJsonSerializer

local_jwt = LocalProxy(lambda: current_app.extensions['jwt'])

@jwt.user_handler
def load_user(payload):
    from ..account import AccountService
    if payload["id"]:
        return AccountService().get_one(payload["id"])

class Signer(object):
    def __init__(self, jwt=local_jwt, serializer=None):
        self.jwt = jwt
        self.serializer = serializer or TokenJsonSerializer()

    def sign(self, account):
        token = self.jwt.encode_callback(self.serializer.emit_json_for(account))
        return {
            "account": account.serializing_with('TokenJsonSerializer'),
            "token": token
        }


