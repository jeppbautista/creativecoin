from flask_wtf import FlaskForm
import wtforms as wtf
from wtforms import validators
from wtforms.widgets import TextArea


class Contact(FlaskForm):
    """
    Form class for the contacts field in contact-us.html
    """
    email = wtf.StringField(
        "Email:",
        validators=[
            validators.InputRequired(),
            validators.Email(),
            validators.Length(max=128)
        ],
        render_kw={
            "class": "form-control mb-1 field",
            "placeholder": "juandelacruz@testing.com"
        }
    )

    name = wtf.StringField(
        "Name:",
        validators=[
            validators.InputRequired(),
        ],
        render_kw={
            "class": "form-control mb-1 field",
            "placeholder": "Juan Dela Cruz"
        }
    )

    message = wtf.StringField(
        "Message:",
        validators=[
            validators.InputRequired(),
        ],
        render_kw={
            "class": "form-control rounded-0",
            "style": "resize:none"
        },
        widget=TextArea()
    )

    contact = wtf.SubmitField(
        "Contact Us",
        render_kw={
            "class": "c-yellow btn btn-light"
        }
    )
