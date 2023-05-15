from functools import wraps
from flask import g, request, abort
import hmac
import hashlib
from .utils import get_config_value
import requests


def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request is None:
            return abort(400)

        if 'TPT-SIGN' not in request.headers:
            return abort(403)

        signature_request = request.headers['TPT-SIGN']

        secret = get_config_value('TPT_SECRET')

        signature = hmac.new(secret.encode('utf8'), request.data, digestmod=hashlib.sha512)
        signature_calculated = signature.hexdigest()

        if signature_request != signature_calculated:
            return abort(403)

        return f(*args, **kwargs)
    return decorated_function