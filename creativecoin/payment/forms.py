from flask_wtf import FlaskForm

import wtforms as wtf
from wtforms import validators
from wtforms.widgets.html5 import NumberInput

class Payment(FlaskForm):
    quantity = wtf.IntegerField('Quantity',
        validators=[
            validators.InputRequired()
        ],
        render_kw={
            'id': 'quantity',
            'class': 'form-control'
        },
        widget=NumberInput()
    )
    item_name = wtf.StringField('Item name',
        validators=[
            validators.InputRequired()
        ],
        render_kw={
           'style': 'display:none',
           'class': 'display-none'
       }
    )
    amount_php = wtf.StringField('Amount in PHP',
        validators=[
            validators.InputRequired()
        ],
        render_kw={
            'style': 'display:none',
            'class': 'display-none'
        }
    )
    amount_usd = wtf.StringField('Amount in USD',
        validators=[
            validators.InputRequired()
        ],
        render_kw={
            'style': 'display:none',
            'class': 'display-none'
        }
    )
    payment_category = wtf.StringField("Payment category")
    reference = wtf.StringField('Reference ID',
        validators=[
            validators.InputRequired()
        ],
        render_kw={
            'id': 'refid',
            'class': 'form-control',
            'placeholder': 'Reference ID here'
        }
    )
