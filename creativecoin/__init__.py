from flask import Flask, g, redirect, request, render_template, session
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user
)
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman

from elasticsearch import Elasticsearch

from datetime import datetime, timedelta
import logging
import os
import traceback

def setup_logging():
    """
        Initialize logging instance.
    """
    format_str = "[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(message)s"
    file_handler = logging.FileHandler("logs/{:%Y-%m-%d}.log".format(datetime.now()))
    formatter = logging.Formatter(format_str)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)

    app.logger.addHandler(file_handler)
    app.logger.addHandler(stream_handler)

"""======Content Security Policies======"""
csp = {
    'script-src': [
        '\'self\''
        , 'cdnjs.cloudflare.com'
        , '*.gstatic.com'
        , '*.jquery.com'
        , '*.googleapis.com'
        , 'cdn.deliver'
        , 'https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js'
        , 'https://threejs.org/examples/js/libs/stats.min.js'
        , 'https://unpkg.com/aos@2.3.1/dist/aos.css'
        , 'https://unpkg.com/aos@2.3.1/dist/aos.js'
        , '*.clocklink.com'
    ]
}

os.environ["TZ"]="Asia/Manila"

app = Flask(__name__)

Talisman(app, 
    content_security_policy=csp, 
    content_security_policy_nonce_in=['script-src']
)

app.secret_key = app.config['SECRET_KEY']
app.config['SESSION_TYPE'] = "filesystem"
app.url_map.strict_slashes = False

"""======Loads the proper configuration file depending on the environment======"""
app.config['ENV'] = "production" if os.environ['SERVER_NAME'] == "creativecoin.net" else "dev"
if app.config['ENV'] == "production":
    app.config.from_object('creativecoin.config.ProdConfig')
else:
    app.config.from_object('creativecoin.config.DevConfig')

setup_logging()

"""======Initialization of Flask_Login======"""
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

"""======Initialization of Database instances======"""
db = SQLAlchemy(app)
migrate = Migrate(app, db)
es = Elasticsearch([app.config["ES_HOST"]])

"""======Registration of Blueprints/Modules======"""
from creativecoin.views import main
from creativecoin.admin.views import adm
from creativecoin.blockchain.views import node
from creativecoin.dashboard.views import dash
from creativecoin.login.views import auth
from creativecoin.payment.views import pay
from creativecoin.api.views import api
from creativecoin.dev.views import dev

app.register_blueprint(main)
app.register_blueprint(auth)
app.register_blueprint(dash)
app.register_blueprint(pay)
app.register_blueprint(adm)
app.register_blueprint(node)
app.register_blueprint(api)
app.register_blueprint(dev)

from creativecoin import models

import wtforms_json
wtforms_json.init()

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


@app.before_request
def before_request():

    ################
    # Flask inactivity
    #################
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=15)
    # session.modified = True
    # g.user = current_user

    ################
    # ES Initialization
    #################

    es = Elasticsearch([app.config["ES_HOST"]])
    if not es.ping():
        return render_template("error/500.html", code=500)

    ################
    # Force redirect to https
    #################

    if request.url.startswith('http://') and app.config['ENV'] == "production":
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)

@app.teardown_appcontext
def shutdown_session(exception):
    if exception:
        db.session.rollback()
    db.session.remove()
