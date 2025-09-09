from sanic import Blueprint, Sanic
from ..logic.auth.login import g_auth_login


def register_handlers(app: Sanic):
    auth = Blueprint('auth', url_prefix='/auth')
    auth.add_route(g_auth_login, '/login', methods=['GET'])

    app.blueprint(auth)