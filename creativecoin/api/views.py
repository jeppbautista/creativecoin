from flask import Blueprint, redirect, request, url_for, render_template, jsonify

from creativecoin.helper import utils
from creativecoin import app, db, models

import traceback

import os

api = Blueprint("api", __name__)

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
   

