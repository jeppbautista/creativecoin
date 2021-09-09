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


@api.route("/api/login/callback_signup", methods=["GET", "POST"], strict_slashes=False)
def login_callback_signup():
    data = request.get_json()
    signupform = Signup.from_json(data, csrf_enabled=False)

    app.logger.error("APP INFO - /api/login/callback_signup")

    if signupform.validate():
        app.logger.error("APP INFO - FORM is valid")
        formdata = dict(signupform.data)

        del formdata["register"]

        ref = formdata["referrer"]
        if ref[0:5] == "https":
            formdata["referrer"] = ref.split("login?")[-1]

        formdata["referrer"] = utils.encode_referral_id(formdata["referrer"])

        try:
            user = models.User(**formdata)
            # queries.add(user)
            # queries.commit_db()

            app.logger.error("APP INFO - User was created")

            wallet = models.Wallet(user_id=user.id, wallet_id=utils.generate_wallet_id(str(user.id)))
            # queries.add(wallet)

            referrer_wallet = queries.get_wallet(user_id=user.referrer)
            referrer_wallet.referral = referrer_wallet.referral + (referrer_wallet.free_mined*decimal.Decimal(app.config["REFERRAL_PCT"]))
            # queries.commit_db()

            app.logger.error("APP INFO - Wallet was created")
            app.logger.error(str(wallet.__dict__))

            email = formdata["email"]
            firstname = formdata["firstname"]

        except Exception as e:
            pass

    return jsonify(message=str(formdata), level="info")



@api.route("/api/login/is_auth")
def login_is_auth():
    if current_user.is_authenticated:
        return jsonify(status=True, user=str(current_user.__dict__))
    return jsonify(status=False)


@api.route("/api/login/logout")
def login_logout():
    """
    Mobile endpoint for logging out
    """
    logout_user()
    return jsonify(message="User logged out", level="info"), 200


@api.route("/api/wallet/qr", methods=["GET", "POST"], strict_slashes=False)
def wallet_qr():
    try:
        app.logger.error("APP INFO - /api/wallet/qr")
        data = {"wallet": ""}
        app.logger.error("TEST")
    
        data = request.get_json()
        if data["wallet"] == "" or data["wallet"] is None:
            return jsonify(message="Incomplete params", level="error"), 400

        wallet_address = utils.generate_wallet_id(data["wallet"])
        png_path = os.path.join(os.getcwd(), "creativecoin\\static\\image\\qr\\{}.png".format(wallet_address))
        if not os.path.isfile(png_path):
            import pyqrcode
            qr = pyqrcode.create(wallet_address)
            qr.png(png_path, scale=8)

        return jsonify(wallet="static/image/qr/{}.png".format(wallet_address), level="info")
    except Exception as e:
        app.logger.error(traceback.format_exc())
        return jsonify(message="Something went wrong", level="error")
   

@api.route("/api/error")
def api_error():
    data = request.get_json()
    app.logger.error(data["message"])
    return "Logged"