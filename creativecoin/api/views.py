from flask import Blueprint, redirect, request, url_for, render_template, jsonify
from flask_login import current_user, login_user, logout_user

from creativecoin.helper import utils
from creativecoin import app, db, models
from creativecoin.email import EmailSender
from creativecoin.error import ERROR_MESSAGE_LOOKUP
from creativecoin.helper import utils
from creativecoin.login import helpers, queries
from creativecoin.login.forms import Login, Signup
from creativecoin import app, db, login_manager, models

import traceback

import os

api = Blueprint("api", __name__)


@api.route("/api/login/callback_login", methods=["GET", "POST"], strict_slashes=False)
def login_callback_login():
    data = request.get_json()
    loginform = Login.from_json(data, csrf_enabled=False)

    app.logger.error("APP INFO - /api/login/callback_login")

    if loginform.validate():
        app.logger.error("APP INFO - FORM is valid")
        formdata = dict(loginform.data)

        user = queries.get_user(email = formdata["email"])

        if user is None or not user.validate_password(formdata["password"]):
            app.logger.error("APP ERROR - PASSWORD is invalid")
            return jsonify(message="PASSWORD is invalid", level="error"), 500
        
        login_user(user)
        app.logger.error("APP INFO - user logged in")

        return jsonify(message="LOGIN successfull", level="info"), 200

    else:
        app.logger.error("APP ERROR - FORM is invalid")
        return jsonify(message="FORM is invalid", level="error"), 500


@api.route("/api/login/is_auth")
def login_is_auth():
    if current_user is not None:
        return jsonify(status=True)
    return jsonify(status=False)


@api.route("/api/wallet/qr", methods=["GET", "POST"], strict_slashes=False)
def wallet_qr():
    try:
        data = {"wallet": ""}
        app.logger.error("TEST")
    
        data = request.get_json()
        if data["wallet"] == "" or data["wallet"] is None:
            return jsonify(message="Incomplete params"), 400

        wallet_address = utils.generate_wallet_id(data["wallet"])
        png_path = os.path.join(os.getcwd(), "creativecoin\\static\\image\\qr\\{}.png".format(wallet_address))
        if not os.path.isfile(png_path):
            import pyqrcode
            qr = pyqrcode.create(wallet_address)
            qr.png(png_path, scale=8)

        return jsonify(wallet="static/image/qr/{}.png".format(wallet_address))
    except Exception as e:
        app.logger.error(traceback.format_exc())
        return ""
   

@api.route("/api/error")
def api_error():
    data = request.get_json()
    app.logger.error(data["message"])
    return "Logged"