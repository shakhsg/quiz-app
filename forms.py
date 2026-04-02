from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class RegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name  = StringField('Last Name',  validators=[DataRequired()])
    email      = EmailField('Email Address', validators=[DataRequired(), Email()])
    password   = PasswordField('Password', validators=[
                     DataRequired(), Length(min=8, message='Minimum 8 characters required')])
    confirm    = PasswordField('Confirm Password', validators=[
                     DataRequired(), EqualTo('password', message='Passwords do not match')])
    submit     = SubmitField('Create Account')


class LoginForm(FlaskForm):
    email    = EmailField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password',  validators=[DataRequired()])
    submit   = SubmitField('Sign In')


class TOTPForm(FlaskForm):
    """
    Used both for the MFA login challenge and the disable-MFA form.
    Accepts a 6-digit TOTP code or an 8-character backup code.
    """
    code   = StringField('Code', validators=[
                 DataRequired(),
                 Length(min=6, max=8, message='Enter a 6-digit code or 8-character backup code')])
    submit = SubmitField('Verify')


class SetupMFAForm(FlaskForm):
    """Confirm the first code during TOTP setup to prove the app is configured correctly."""
    code   = StringField('Authenticator Code', validators=[
                 DataRequired(),
                 Length(min=6, max=6, message='Enter the 6-digit code from your authenticator app')])
    submit = SubmitField('Enable MFA')
