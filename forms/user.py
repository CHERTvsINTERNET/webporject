from flask_wtf import FlaskForm
from wtforms import (BooleanField, EmailField, IntegerField, PasswordField,
                     StringField, SubmitField, TextAreaField)
from wtforms.validators import DataRequired


class UserRegisterForm(FlaskForm):
    name = StringField('Имя Пользователя', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField(
        'Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Регистрация')


class UserLoginForm(FlaskForm):
    email = EmailField("Почта", validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
