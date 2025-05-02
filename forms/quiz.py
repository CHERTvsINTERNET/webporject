from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import (BooleanField, EmailField, FileField, IntegerField,
                     PasswordField, StringField, SubmitField, TextAreaField)
from wtforms.validators import DataRequired


class QuizAddForm(FlaskForm):
    quiz_name = StringField('Название', validators=[DataRequired()])
    quiz_description = TextAreaField('Описание', validators=[DataRequired()])
    quiz_theme = StringField('Тема', validators=[DataRequired()])
    quiz_cover = FileField("Картинка", validators=[FileAllowed(
        ['jpg', 'png'], 'TOLKO KARTINKI'), DataRequired()])
    submit = SubmitField('Перейти к настройке')


class QuizSettingsForm(FlaskForm):
    quiz_name = StringField('Название', validators=[DataRequired()])
    quiz_description = TextAreaField('Описание', validators=[DataRequired()])
    submit = SubmitField('Сохранить')
