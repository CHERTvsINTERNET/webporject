from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import (BooleanField, FileField, IntegerField, PasswordField,
                     RadioField, StringField, SubmitField, TextAreaField)
from wtforms.validators import DataRequired


class QuestionAdd(FlaskForm):
    question = StringField("Вопрос", validators=[DataRequired()])
    picture = FileField("Картинка", validators=[FileAllowed(
        ['jpg', 'png'], 'TOLKO KARTINKI'), DataRequired()])
    is_answer1 = BooleanField("Ответ 1")
    is_answer2 = BooleanField("Ответ 2")
    is_answer3 = BooleanField("Ответ 3")
    is_answer4 = BooleanField("Ответ 4")

    answer1_text = StringField()
    answer2_text = StringField()
    answer3_text = StringField()
    answer4_text = StringField()

    true_answer = RadioField(
        "", choices=[(1, "Ответ 1"), (2, "Ответ 2"), (3, "Ответ 3"), (4, "Ответ 4")])

    submit = SubmitField("Применить")


class QuestionRedact(FlaskForm):
    question = StringField("Вопрос", validators=[DataRequired()])
    picture = FileField("Картинка")

    is_answer1 = BooleanField("Ответ 1")
    is_answer2 = BooleanField("Ответ 2")
    is_answer3 = BooleanField("Ответ 3")
    is_answer4 = BooleanField("Ответ 4")

    answer1_text = StringField("Ответ 1")
    answer2_text = StringField("Ответ 2")
    answer3_text = StringField("Ответ 3")
    answer4_text = StringField("Ответ 4")

    true_answer = RadioField(
        "", choices=[(1, "Ответ 1"), (2, "Ответ 2"), (3, "Ответ 3"), (4, "Ответ 4")])

    submit = SubmitField("Применить")
