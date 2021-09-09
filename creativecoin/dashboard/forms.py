from flask_wtf import FlaskForm
import wtforms as wtf
from wtforms.fields import html5
from wtforms import validators
from flask_login import current_user
from creativecoin.models import Wallet


def validate_wallet(form, field):
    current_wallet = Wallet.query.filter(Wallet.wallet_id == field.data).first()
    if not current_wallet:
        raise validators.ValidationError("Wallet address does not exist")

    if current_wallet.user_id == current_user.id:
        raise validators.ValidationError("Sending to own address is not allowed")

def validate_amount(form, field):
    print(form.balance.__dict__)
    if field.data > form.balance.data:
        raise validators.ValidationError("Insufficient balance")


class Send(FlaskForm):
    balance = wtf.IntegerField(
        "Source wallet (CCN)",
        render_kw={
            "class": "form-control",
            "readonly": ""
        }
    )
    amount = html5.IntegerField(
        "Amount:",
        validators=[
            validators.NumberRange(min=100, message="Minimum of 100 CCN is required."),
            validators.InputRequired(),
            validate_amount
        ],
        render_kw={
            "class": "send-input form-control",
            "placeholder": "Amount of CCN to send"
        },
    )
    to_wallet = wtf.StringField(
        "Send to:",
        validators=[
            validators.InputRequired(),
            validate_wallet
        ],
        render_kw={
            "class": "send-input form-control",
            "placeholder": "Enter CCN wallet address"
        }
    )
    sourcewallet = wtf.SelectField(
        "Source wallet (CCN):",
        validators=[
            validators.InputRequired()
        ],
        choices=[
            ("0", "System mined (CCN)"),
            ("1", "Free mined (CCN)"),
            ("2", "Received (CCN)"),
        ],
        render_kw={
            "class": "form-control send-input"
        }
    )
    submit = wtf.SubmitField(
        "Submit",
        render_kw={
            "class": "btn btn-block c-light-blue c-text-fafa"
        }
    )

