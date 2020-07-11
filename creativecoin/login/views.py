from flask import Blueprint, redirect, request, url_for, render_template
from flask_login import current_user, login_user, logout_user
import requests
import smtplib
from sqlalchemy.exc import IntegrityError

from creativecoin.dashboard.views import dash
from creativecoin.email import EmailSender
from creativecoin.error import ERROR_MESSAGE_LOOKUP
from creativecoin.login import helpers
from creativecoin.login.forms import Login, Signup
from creativecoin import app, db, login_manager, models

auth = Blueprint('auth', __name__)

@auth.route('/confirm/<token>', strict_slashes=False)
def confirm_email(token):
    try:
        email = helpers.confirm_token(token)
    except Exception as e:
        app.logger.error(e)
        return render_template('email/token.html', 
            message="This is an invalid confirmation link or it has expired already. You can request for another link.", 
            button="Resend email",
            href="#")

    user = models.User.query.filter_by(email=email).first_or_404()

    if user.emailverified:
        return render_template('email/token.html', 
            message="Account is already verified. You can now use CreativeCoin and all its features.", 
            button="Get Started",
            href=url_for("auth.login"))

    else:
        user.emailverified = True
        db.session.add(user)
        db.session.commit()
        app.logger.info("Account has been confirmed")
        return render_template('email/token.html', 
            message="Your email is now verified. You can now use CreativeCoin and all its features.", 
            button="Get Started",
            href=url_for("auth.login"))

    return redirect(url_for('dash.wallet'))


@auth.route('/login', methods=['GET'], strict_slashes=False)
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dash.wallet'))
        
    loginform = Login()
    signupform = Signup()
    
    data = {}
    data['last_action'] = request.args.get('last_action', '')
    data['error'] = request.args.get('error', "").split(" ")

    data['error'][:] = [ERROR_MESSAGE_LOOKUP.get(e, ERROR_MESSAGE_LOOKUP['na']) for e in data['error']]
    data['error'][:] = [err for err in data['error'] if err]

    return render_template('login/login.html', loginform=loginform, signupform=signupform, data=data)


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/callback_login', methods=['GET', 'POST'], strict_slashes=False)
def callback_login():
    redirect_url = request.form.get('redirect', None)
    loginform = Login(request.form)
    signupform = Signup()

    data = {
        'last_action': 'login',
        'error': ''
    }

    if loginform.validate():
        formdata = dict(loginform.data)

        del formdata['login']
        del formdata['csrf_token']

        user = models.User.query.filter_by(email=formdata["email"]).first()

        if user is None or not user.validate_password(formdata["password"]):
            data['error'] = 'pass_email_error'
            return redirect(url_for('auth.login', **data))
        
        login_user(user)

        if not redirect_url:
            return redirect(url_for('dash.wallet'))
        else:
            return redirect(redirect_url)

    else:
        data['error'] = "login_form_error"

    return redirect(url_for('auth.login', **data))


@auth.route('/callback_signup', methods=['GET','POST'], strict_slashes=False)
def callback_signup():

    loginform = Login()
    signupform = Signup(request.form)

    data = {
        'last_action': 'signup',
        'error': ''
    }

    if signupform.validate():
        formdata = dict(signupform.data)

        del formdata['register']
        del formdata['csrf_token']

        user = models.User(**formdata)

        db.session.add(user)
        try:
            db.session.commit()

            wallet = models.Wallet(user_id = user.id)
            db.session.add(wallet)
            db.session.commit()
            
            token = helpers.generate_email_token(formdata['email'])
            params = {
                "verification_link": "http://{root_url}/confirm/{token}".format(root_url = app.config['SERVER_NAME'], token = token),
                "firstname": formdata['firstname']
            }
            
            mail = EmailSender()
            body = mail.prepare_body(params, path="verify-email.html")
            if not mail.send_mail(formdata['email'], "Confirm your email address", body):
                return "Email sending failed"
            
            return redirect(url_for('auth.verify_email'))
            
        except IntegrityError as e:
            app.logger.error(str(e.__cause__))
            if 'Duplicate' in str(e.__cause__):
                data['error'] = "signup_email_exists"
            db.session.rollback()
        except Exception as e:
            app.logger.error(e)
            data['error'] = "default_error"
            db.session.rollback()

    elif signupform.errors:
        app.logger.error(signupform.errors)
        data['error'] = "signup_form_error"

    else:
        return redirect(url_for('auth.login'))

    return redirect(url_for('auth.login', **data))


@auth.route('/verify-email')
def verify_email():
    return render_template('email/verification-sent.html')


@login_manager.user_loader
def load_user(id):
    return models.User.query.get(int(id))


@auth.route('/logintest')
def test():
    # return render_template('email/token.html', 
    #         message="Account is already verified. You can now use CreativeCoin and all its features.", 
    #         button="Login",
    #         href=url_for("auth.login"))
    headers = {'content-type': 'application/json'}
    return requests.post('/login', data={"test":"foo"})