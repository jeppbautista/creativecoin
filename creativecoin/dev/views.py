from flask import Blueprint, redirect, request, url_for, render_template
from flask_login import current_user, login_user, logout_user

import decimal
import requests
import smtplib
from sqlalchemy.exc import IntegrityError
import traceback

from creativecoin.dashboard.views import dash
from creativecoin.email import EmailSender
from creativecoin.error import ERROR_MESSAGE_LOOKUP
from creativecoin.helper import utils
from creativecoin.login import helpers, queries

from creativecoin.login.forms import Login, Signup
from creativecoin import app, db, login_manager, models

dev = Blueprint("dev", __name__)


@app.route("/dev/refresh_tables", methods=["GET", "POST"])
def drop_tables():
    password = request.form.get("password")
    if password == app.config["SECRET_KEY"]:
        db.drop_all()
        db.create_all()

        users = [
            {
                "email": "admin@creativecoin.net",
                "password": "cEBzc3dvcmQxMjMh",
                "firstname": "Admin",
                "lastname": "Admin",
                "phonenumber": "12345678900",
                "referrer": 1,
                "emailverified": True,
                "is_admin": True,
            }
        ]

        wallets = [
            {
                "user_id": 1,
                "wallet_id": "c4ca4238a0b923820dcc509a6f75849b",
                "free_mined": 100,
                "mined": 100,
                "received": 0,
                "referral": 0,
                "total_balance": 200
            }
        ]

        for user, wallet in zip(users, wallets):
            u = models.User(**user)
            w = models.Wallet(**wallet)
            db.session.add(u)
            db.session.add(w)
            db.session.commit()
    
        return "refreshed"
    return "Failed"