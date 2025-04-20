from flask_wtf import FlaskForm
from wtforms import (BooleanField, EmailField, IntegerField, PasswordField,
                     StringField, SubmitField, TextAreaField)
from wtforms.validators import DataRequired


class QuizAddForm(FlaskForm):
    quiz_name = StringField('Название', validators=[DataRequired()])
    quiz_description = TextAreaField('Описание', validators=[DataRequired()])
    submit = SubmitField('Перейти к настройке')


class QuizSettingsForm(FlaskForm):
    quiz_name = StringField('Название', validators=[DataRequired()])
    quiz_description = TextAreaField('Описание', validators=[DataRequired()])
    submit = SubmitField('Сохранить')
