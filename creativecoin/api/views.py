from flask import Blueprint, redirect, request, url_for, render_template, jsonify

from creativecoin.helper import utils
from creativecoin import app, db, models

import os

api = Blueprint("api", __name__)

@api.route("/api/wallet/qr", methods=["GET"], strict_slashes=False)
def wallet_qr():
    data = {}
    
    data["wallet"] = request.args.get("wallet", "")
    if data["wallet"] == "":
        return jsonify(message="Incomplete params"), 400

    wallet_address = utils.generate_wallet_id(data["wallet"])
    png_path = os.path.join(os.getcwd(), f"creativecoin\\static\\image\\qr\\{wallet_address}.png")
    if not os.path.isfile(png_path):
        import pyqrcode
        qr = pyqrcode.create(wallet_address)
        qr.png(png_path, scale=8)

    return jsonify(wallet=f"static/image/qr/{wallet_address}.png")

