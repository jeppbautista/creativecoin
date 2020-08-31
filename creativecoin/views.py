from flask import Blueprint, redirect, request, url_for, render_template, jsonify
from flask_login import login_required

import json
main = Blueprint('main', __name__)

from creativecoin import app
import os

env = app.config['ENV']

def subdomain(rule='/', subdomain=''):
    if app.config['ENV'] == "production":
        return dict(rule=rule, subdomain=subdomain)
    else:
        if rule == "/": rule = ""
        return dict(rule=rule+'/'+subdomain, subdomain='')


@app.route('/', subdomain='', strict_slashes=False)
def index():
    return render_template('home/home.html')
    # return render_template('index/index.html')
    

@app.route(rule='/cdn', strict_slashes=False)
def cdn():
    return "CDN"
    

@app.route(rule='/my', strict_slashes=False)
def my():
    return "My"
    
    
@app.route(rule='/news', strict_slashes=False)
def news():
    return "News"


@app.route(rule="/get-in-touch", strict_slashes=False)
def contact_us():
    return render_template("contact-us.html")


@app.route(rule='/test', strict_slashes=False, methods=["GET", "POST"])
def test():
    return  "ssss"


@app.errorhandler(503)
def internal_error(e):
    return render_template("error/503.html")

@app.errorhandler(500)
def internal_error2(e):
    return render_template("error/500.html")

@app.errorhandler(404)
def not_found(e):
    return render_template("error/404.html")

@app.errorhandler(400)
def bad_request(e):
    return render_template("error/400.html")