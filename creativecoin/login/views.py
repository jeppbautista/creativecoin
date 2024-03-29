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

auth = Blueprint("auth", __name__)


@auth.route("/confirm/<token>", strict_slashes=False)
def confirm_email(token):
    """
    Renders the email confirmation page.

    Parameters:
    -----------
    token (str): Unique token generated in `helpers.generate_email_token`
    """
    app.logger.error("INFO - /confirm/{}".format(token))
    try:
        email = helpers.confirm_token(token)
        app.logger.error("INFO - TOKEN confirmation for: {}".format(email))
    except Exception as e:
        app.logger.error(traceback.format_exc())
        app.logger.error("ERROR - INVALID TOKEN")
        return render_template("email/token.html",
            message="This is an invalid confirmation link or it has expired already. You can request for another link once you log-in.",
            button="Login",
            href="auth.login",
            title="Invalid token - CreativeCoin")

    user = queries.get_user(email=email)

    if user.emailverified:
        app.logger.error("INFO - TOKEN ALREADY CONFIRMED for: {}".format(email))
        return render_template("email/token.html",
            message="Account is already verified. You can now use CreativeCoin and all its features.",
            button="Get Started",
            href=url_for("auth.login"),
            title="Token verified - CreativeCoin")
    else:
        user.emailverified = True
        queries.add(user)
        queries.commit_db()
        app.logger.error("INFO - TOKEN CONFIRMED for: {}".format(email))
        return render_template("email/token.html",
            message="Your email is now verified. You can now use CreativeCoin and all its features.",
            button="Get Started",
            href=url_for("auth.login"),
            title="Token verified - CreativeCoin")

    return redirect(url_for("dash.wallet"))


@auth.route("/login", methods=["GET"], strict_slashes=False)
def login():
    """
    Renders the login page
    """
    if current_user.is_authenticated:
        return redirect(url_for("dash.wallet"))

    loginform = Login()
    signupform = Signup()

    data = {}
    data["last_action"] = request.args.get("last_action", "")
    data["error"] = request.args.get("error", "")

    data["error"] = ERROR_MESSAGE_LOOKUP.get("error", ERROR_MESSAGE_LOOKUP["default_error"])
    return render_template("login/login.html", loginform=loginform, signupform=signupform, data=data, title="Login - CreativeCoin")


@auth.route("/logout")
def logout():
    """
    Endpoint for logging out
    """
    logout_user()
    return redirect(url_for("index"))


@auth.route("/callback_login", methods=["GET", "POST"], strict_slashes=False)
def callback_login():
    """
    Endpoint for logging in

    Parameters (form):
    ------------------
    email (str): email of the user
    password (str): hashed password of the user
    login (str): a token generated to verify if the form was submitted
    """
    redirect_url = request.form.get("redirect", None)
    loginform = Login(request.form)
    signupform = Signup()

    app.logger.error("INFO - /callback_login")
    # app.logger.error("INFO - {}".format(str(request.form)))

    data = {
        "last_action": "login",
        "error": ""
    }

    if loginform.validate():
        app.logger.error("INFO - FORM is valid")
        formdata = dict(loginform.data)

        del formdata["login"]
        del formdata["csrf_token"]

        user = queries.get_user(email = formdata["email"])

        if user is None or not user.validate_password(formdata["password"]):
            app.logger.error("ERROR - PASSWORD is invalid")
            data["error"] = "pass_email_error"
            return redirect(url_for("auth.login", **data))

        login_user(user, remember=False)
        app.logger.error("INFO - user logged in")

        if not redirect_url:
            return redirect(url_for("dash.wallet"))
        else:
            return redirect(redirect_url)

    else:
        app.logger.error("ERROR - FORM is invalid")
        app.logger.error(loginform.errors)
        data["error"] = "login_form_error"

    return redirect(url_for("auth.login", **data))


@auth.route("/callback_signup", methods=["GET", "POST"], strict_slashes=False)
def callback_signup():
    """
    Endpoint for signing-up

    Parameters (form):
    ------------------
    email (str): email of the user
    password (str): hashed password of the user
    firstname (str): first name of the user
    lastname (str): last name of the user
    phonenumber (str): phone number of the user
    referrer (str): the referrer of the user
    register (str): a token generated to verify if the form was submitted
    """
    loginform = Login()
    signupform = Signup(request.form)

    app.logger.error("INFO - /callback_signup")
    # app.logger.error("INFO - {}".format(str(request.form)))

    data = {
        "last_action": "signup",
        "error": ""
    }

    if signupform.validate():
        app.logger.error("INFO - FORM is valid")
        formdata = dict(signupform.data)

        del formdata["register"]
        del formdata["csrf_token"]
        formdata["referrer"] = utils.encode_referral_id(formdata["referrer"])

        try:
            user = models.User(**formdata)
            queries.add(user)
            queries.commit_db()

            app.logger.error("INFO - User was created")
            wallet = models.Wallet(user_id=user.id, wallet_id=utils.generate_wallet_id(str(user.id)))
            queries.add(wallet)

            referrer_wallet = queries.get_wallet(user_id=user.referrer)
            referrer_wallet.referral = referrer_wallet.referral + (referrer_wallet.free_mined*decimal.Decimal(app.config["REFERRAL_PCT"]))
            queries.commit_db()

            app.logger.error("INFO - Wallet was created")
            app.logger.error(str(wallet.__dict__))

            email = formdata["email"]
            firstname = formdata["firstname"]

            if not _verify_email(email, firstname):            
                app.logger.error("ERROR - Email sending failed")
                return render_template("email/token.html",
                    message="Email sending failed. Please contact administrator",
                    button="Contact us",
                    href=url_for("contact_us"))

            return redirect(url_for("auth.verify_email"))

        except IntegrityError as e:
            app.logger.error(traceback.format_exc())
            if "Duplicate" in str(e.__cause__):
                data["error"] = "signup_email_exists"
            db.session.rollback()
        except Exception as e:
            app.logger.error(traceback.format_exc())
            data["error"] = "default_error"
            db.session.rollback()

    elif signupform.errors:
        app.logger.error("ERROR - There are ERRORS in the form")
        app.logger.error(signupform.errors)
        data["error"] = "signup_form_error"

    else:
        app.logger.error("ERROR - FORM is invalid")
        return redirect(url_for("auth.login"))

    return redirect(url_for("auth.login", **data))


@auth.route("/verify-email")
def verify_email():
    """
    Renders the verification sent page
    """
    app.logger.error("INFO - /verify-email")
    return render_template("email/verification-sent.html", 
        title="Email verified - CreativeCoin")


@auth.route("/verify-email-2")
def verify_email_2():
    """
    Renders the verification failed page
    """
    app.logger.error("INFO - /verify-email-2")
    email = current_user.email
    firstname = current_user.firstname

    app.logger.error("INFO - {}".format(email))

    if _verify_email(email, firstname):
        return redirect(url_for("auth.verify_email"))
    else:
        app.logger.error("ERROR - Email sending failed")
        return render_template("email/token.html",
            message="Email sending failed. Please contact administrator",
            button="Contact us",
            href=url_for("contact_us"),
            title="Email verified - CreativeCoin")


@login_manager.user_loader
def load_user(id):
    return models.User.query.get(int(id))


@auth.route("/logintest")
def test():
    ref = "XKJDKLSJLDKJD"
    x = utils.encode_referral_id(ref)
    return str(x)


def _verify_email(email, firstname):
    """
    Generates the token and sends the email for verification

    Parameters:
    -----------
    email (str): email of the recepient
    firstname (str): first name of the recepient

    Returns:
    --------
    boolean: True if the email sending is successful else False
    """
    token = helpers.generate_email_token(email)
    params = {
        "verification_link": "http://{root_url}/confirm/{token}".format(root_url = app.config["SERVER_NAME"], token = token),
        "firstname": firstname
    }
            
    mail = EmailSender()
    body = mail.prepare_body(params, path="verify-email.html")
    return mail.send_mail(email, "Confirm your email address", body)
        
