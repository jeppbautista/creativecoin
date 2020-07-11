import email_validator

from flask_wtf import FlaskForm

import wtforms as wtf
from wtforms import validators

class Login(FlaskForm):
    email = wtf.StringField('Email', [validators.InputRequired()], 
        render_kw={
            'placeholder': 'Email',
            'class': 'form-control mb-4'
        }
    )
    password = wtf.PasswordField('Password', [validators.InputRequired()], 
        render_kw={
            'placeholder': 'Password',
            'class': 'form-control mb-4'
        }
    )
    login = wtf.SubmitField('Sign in', 
        render_kw={
            'class': 'btn btn-light btn-block mt-2 mb-2 waves-effect waves-light'
        }
    )

class Signup(FlaskForm):
    email = wtf.StringField('Email:', 
        validators=[
            validators.InputRequired(), 
            validators.Email(),
            validators.Length(max=128)
        ],
        render_kw={
            'id': 'txt-signup__email',
            'placeholder': 'sample@email.com',
            'class': 'form-control'
        }
    )
    password = wtf.PasswordField('Password', 
        validators=[
            validators.InputRequired(), 
            validators.Length(min=8, max=50)
        ],
        render_kw={
            'id': 'txt-signup__password',
            'class': 'form-control'
        }
    )
    firstname = wtf.StringField("First name", 
        validators=[
            validators.InputRequired(),
            validators.Length(max=128)
        ],
        render_kw={
            'id': 'txt-signup__firstname',
            'class': 'form-control'
        }
    )
    lastname = wtf.StringField("Last name", 
        validators=[
            validators.InputRequired(),
            validators.Length(max=128)
        ],
        render_kw={
            'id': 'txt-signup__lastname',
            'class': 'form-control'
        }
    )
    phonenumber = wtf.StringField("Phone number",
        validators=[
            validators.Length(max=20)
        ],
        render_kw={
            'id': 'txt-signup__phone',
            'class': 'form-control'
        }
    )

    register = wtf.SubmitField('register', 
        render_kw={
            'id': 'btn-signup__register',
            'class': 'c-blue btn btn-info btn-block mt-2 mb-2 waves-effect waves-light'
        }
    )