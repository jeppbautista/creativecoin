from flask import Flask, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user
)

import os

app = Flask(__name__)
app.secret_key = app.config['SECRET_KEY']
os.environ['SERVER_NAME'] = "localhost:5000"
app.config['SESSION_TYPE'] = "filesystem"
app.config['ENV'] = "production" if os.environ['SERVER_NAME'] == "creativecoin.net" else "dev"

if app.config['ENV'] == "production":
    app.config.from_object('creativecoin.config.ProdConfig')
else:
    app.config.from_object('creativecoin.config.DevConfig')


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


@app.before_request
def before_request():
    if request.url.startswith('http://') and app.config['ENV'] == "production":
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)


@app.teardown_appcontext
def shutdown_session(exception):
    if exception:
        db.session.rollback()
    db.session.remove()


db = SQLAlchemy(app)
migrate = Migrate(app, db)

from creativecoin.views import main
from creativecoin.admin.views import adm
from creativecoin.login.views import auth
from creativecoin.dashboard.views import dash
from creativecoin.payment.views import pay

app.register_blueprint(main)
app.register_blueprint(auth)
app.register_blueprint(dash)
app.register_blueprint(pay)

app.register_blueprint(adm)

from creativecoin import models



