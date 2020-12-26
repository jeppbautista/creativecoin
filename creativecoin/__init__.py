from flask import Flask, redirect, request, render_template
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

from datetime import datetime
import logging
import os
import traceback

def setup_logging():
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


app = Flask(__name__)

Talisman(app, 
    content_security_policy=csp, 
    content_security_policy_nonce_in=['script-src']
)
app.secret_key = app.config['SECRET_KEY']
app.config['SESSION_TYPE'] = "filesystem"
app.config['ENV'] = "production" if os.environ['SERVER_NAME'] == "creativecoin.net" else "dev"
app.url_map.strict_slashes = False

os.environ["TZ"]="Asia/Manila"

if app.config['ENV'] == "production":
    app.config.from_object('creativecoin.config.ProdConfig')
else:
    app.config.from_object('creativecoin.config.DevConfig')
    

setup_logging()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

db = SQLAlchemy(app)
migrate = Migrate(app, db)
es = Elasticsearch([app.config["ES_HOST"]])

from creativecoin.views import main
from creativecoin.admin.views import adm
from creativecoin.blockchain.views import node
from creativecoin.dashboard.views import dash
from creativecoin.login.views import auth
from creativecoin.payment.views import pay

app.register_blueprint(main)
app.register_blueprint(auth)
app.register_blueprint(dash)
app.register_blueprint(pay)
app.register_blueprint(adm)
app.register_blueprint(node)

from creativecoin import models

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


@app.before_request
def before_request():
    es = Elasticsearch([app.config["ES_HOST"]])
    if not es.ping():
        return render_template("error/500.html", code=500)

    if request.url.startswith('http://') and app.config['ENV'] == "production":
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)
    

@app.teardown_appcontext
def shutdown_session(exception):
    if exception:
        db.session.rollback()
    db.session.remove()


