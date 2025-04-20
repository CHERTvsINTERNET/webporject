from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import (BooleanField, FileField, IntegerField, PasswordField,
                     StringField, SubmitField, TextAreaField)
from wtforms.validators import DataRequired


class QuestionAdd(FlaskForm):
    question = StringField("Вопрос", validators=[DataRequired()])
    picture = FileField("Картинка", validators=[
                        DataRequired()])
    is_answer1 = BooleanField("Ответ 1")
    is_answer2 = BooleanField("Ответ 2")
    is_answer3 = BooleanField("Ответ 3")
    is_answer4 = BooleanField("Ответ 4")

    answer1_text = StringField()
    answer2_text = StringField()
    answer3_text = StringField()
    answer4_text = StringField()

    submit = SubmitField("Применить")


class QuestionRedact(FlaskForm):
    question = StringField("Вопрос", validators=[DataRequired()])
    picture = FileField("Картинка")
    is_answer1 = BooleanField("Ответ 1")
    is_answer2 = BooleanField("Ответ 2")
    is_answer3 = BooleanField("Ответ 3")
    is_answer4 = BooleanField("Ответ 4")

    answer1_text = StringField()
    answer2_text = StringField()
    answer3_text = StringField()
    answer4_text = StringField()

    submit = SubmitField("Применить")
