from ..core import jwt
from flask import request, current_app
from werkzeug.local import LocalProxy

local_jwt = LocalProxy(lambda: current_app.extensions['jwt'])

@jwt.user_handler
def load_user(payload):
    from ..account import AccountService
    if payload["id"]:
        return AccountService().get_one(payload["id"])

class Signer(object):
    def __init__(self, jwt=local_jwt):
        self.jwt = jwt

    def sign(self, account):
        return {
            "account": account,
            "token":   self.jwt.encode_callback(account.to_json())
        }


