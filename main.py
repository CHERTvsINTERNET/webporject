import datetime
import os
from random import choice, sample, shuffle

import requests
import sqlalchemy
from flask import (
    Flask, abort, redirect, render_template, request, send_file,
    url_for
)
from flask_login import (
    LoginManager, current_user, login_required,
    login_user, logout_user
)
from PIL import Image
from sqlalchemy import desc
from wtforms.validators import DataRequired

from blueprints import question_image_getter
from data import db_session
from data.passage import association_table_passage
from data.questions import Question
from data.quizzes import Quiz
from data.themes import Theme
from data.themes_in_quiz import AssociationTheme
from data.user import User
from forms.question import QuestionAdd, QuestionRedact
from forms.quiz import QuizAddForm, QuizSettingsForm
from forms.user import UserLoginForm, UserRegisterForm
from objects.information_template import InfTempl

import logging

'''logging.basicConfig(
    filename='information.log',
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)'''

app = Flask(__file__)
app.config['SECRET_KEY'] = 'mega-slohni-sekret-key-voobshe-nikto-ne-dogadaetsa'

login_manager = LoginManager()
login_manager.init_app(app)


def main():
    if not "db" in os.listdir(".") or not os.path.isdir("db"):
        os.makedirs("db")
    if not "instance" in os.listdir(".") or "question_imgs" not in os.listdir("instance"):
        os.makedirs("instance/question_imgs")
    db_session.global_init("./db/blob.db")
    app.register_blueprint(question_image_getter)


@app.route("/login", methods=["GET", "POST"])
def login_page():
    if current_user.is_authenticated:
        logging.warning("Пользователь уже зарегистрирован")
        abort(404)

    form = UserLoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()

        user = db_sess.query(User).filter(
            User.email == form.email.data
        ).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/profile")
        form.password.data = ""
        return render_template(
            "login.html", message="Неверное email или пароль",
            form=form, title="Авторизация"
        )
    return render_template("login.html", form=form, title="Авторизация")


@app.route("/register", methods=["GET", "POST"])
def register_page():
    if current_user.is_authenticated:
        logging.warning("Пользователь не зарегистрирован")
        abort(404)

    form = UserRegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template(
                "register.html", form=form, title="Регистрация",
                message="Пароли не совпадают", current_user=current_user
            )
        db_sess = db_session.create_session()
        # если почта ужесуществует
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template(
                "register.html", form=form, title="Регистрация",
                message="Такая почта уже зарегистрированна", current_user=current_user
            )
        user = User()
        user.name = form.name.data
        user.email = form.email.data
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect("/login")
    return render_template(
        "register.html", form=form, title="Регистрация",
        current_user=current_user
    )


@app.route("/quizzes/add", methods=["GET", "POST"])
def add_quiz():
    if not current_user.is_authenticated:
        return redirect(f"/login")

    form = QuizAddForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        quiz = Quiz()
        quiz.name = form.quiz_name.data
        quiz.description = form.quiz_description.data
        quiz.author_id = current_user.id
        theme_name = form.quiz_theme.data

        theme = db_sess.query(Theme).filter(Theme.name == theme_name).first()
        if theme is None:
            theme = Theme()
            theme.name = theme_name
            db_sess.add(theme)
            db_sess.commit()

        quiz.themes.append(theme)
        db_sess.add(quiz)
        db_sess.commit()
        quiz_id = quiz.id
        os.makedirs(
            os.path.join(
                app.instance_path,
                'question_imgs', f'quiz_{quiz_id}'
            )
        )

        f = Image.open(form.quiz_cover.data)
        f = f.resize((256, 256))

        path = os.path.join(
            app.instance_path,
            'question_imgs',
            f'quiz_{quiz_id}',
            "cover.jpg"
        )

        f.save(path)

        return redirect(f"/quizzes/redact/{quiz_id}/settings")

    return render_template("quiz_pre_redact.html", title="Создание квиза", form=form)


@app.route("/quizzes/redact/<int:id>/settings", methods=["GET", "POST"])
def redact_quiz_settings(id):
    if not current_user.is_authenticated:
        logging.warning("Пользователь не зарегистрирован")
        abort(404)
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).get(id)
    if not quiz or quiz.author_id != current_user.id:
        logging.warning("Пользователь {} не имеет прав на квиз {}".format(quiz.author_id, current_user.id))
        abort(404)
    if quiz.is_available:
        return redirect(f"/quizzes/published/{id}")

    form = QuizSettingsForm()
    if request.method == "GET":
        form.quiz_name.data = quiz.name
        form.quiz_description.data = quiz.description
    else:
        if form.validate_on_submit():
            quiz.name = form.quiz_name.data
            quiz.description = form.quiz_description.data
            db_sess.commit()
    ques = db_sess.query(Question).filter(Question.quiz_id == id)
    return render_template(
        "quiz_settings.html", form=form, title='Настройки квиза',
        questions=ques, quiz=quiz
    )


@app.route("/quizzes/redact/<int:quiz_id>/questions/add", methods=["GET", "POST"])
def add_question(quiz_id):
    if not current_user.is_authenticated:
        logging.warning("Пользователь не зарегистрирован")
        abort(404)
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).get(quiz_id)
    if not quiz or quiz.author_id != current_user.id:
        logging.warning("Пользователь {} не имеет прав на квиз {}".format(quiz.author_id, current_user.id))

        abort(404)
    if quiz.is_available:
        return redirect(f"/quizzes/published/{quiz_id}")

    ques = db_sess.query(Question).filter(Question.quiz_id == quiz_id)
    form = QuestionAdd()
    if form.validate_on_submit():
        if len(
                list(
                    filter(
                        lambda f: f, [form.is_answer1.data, form.is_answer2.data,
                                      form.is_answer3.data, form.is_answer4.data]
                    )
                )
        ) < 2:
            return render_template(
                "question_setting.html",
                message="Должно быть как минимум два ответа", form=form, quiz=quiz, questions=ques
            )

        f = Image.open(form.picture.data)
        f.thumbnail((1270, 720), Image.Resampling.LANCZOS)

        question = Question()
        question.question = form.question.data
        if form.is_answer1.data:
            question.answer1 = form.answer1_text.data
        if form.is_answer2.data:
            question.answer2 = form.answer2_text.data
        if form.is_answer3.data:
            question.answer3 = form.answer3_text.data
        if form.is_answer4.data:
            question.answer4 = form.answer4_text.data

        question.quiz_id = quiz_id
        question.true_answer = form.true_answer.data
        db_sess.add(question)
        db_sess.commit()

        path = os.path.join(
            app.instance_path,
            'question_imgs',
            f'quiz_{quiz_id}',
            f"question_{question.id}.jpg"
        )

        f.save(path)
        db_sess.commit()
        return redirect(f"/quizzes/redact/{quiz_id}/questions/{question.id}")

    return render_template("question_setting.html", form=form, quiz=quiz, questions=ques)


@app.route(
    "/quizzes/redact/<int:quiz_id>/questions/<int:id>",
    methods=["GET", "POST"]
)
def question_redact(quiz_id, id):
    if not current_user.is_authenticated:
        logging.warning("Пользователь не зарегистрирован")
        abort(404)
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).get(quiz_id)
    if not quiz or quiz.author_id != current_user.id:
        logging.warning("Пользователь {} не имеет прав на квиз {}".format(quiz.author_id, current_user.id))
        abort(404)

    if quiz.is_available:
        return redirect(f"/quizzes/published/{id}")

    question = db_sess.query(Question).get(id)
    if quiz_id != question.quiz_id:
        abort(404)

    form = QuestionRedact(true_answer=question.true_answer)
    ques = db_sess.query(Question).filter(Question.quiz_id == quiz_id).all()
    if request.method == 'GET':
        form.question.data = question.question
        form.is_answer1.data = question.answer1 is not None
        form.is_answer2.data = question.answer2 is not None
        form.is_answer3.data = question.answer3 is not None
        form.is_answer4.data = question.answer4 is not None

        if form.is_answer1.data:
            form.answer1_text.data = question.answer1
        if form.is_answer2.data:
            form.answer2_text.data = question.answer2
        if form.is_answer3.data:
            form.answer3_text.data = question.answer3
        if form.is_answer4.data:
            form.answer4_text.data = question.answer4

        return render_template(
            "question_setting.html", form=form, quiz=quiz,
            questions=ques, pic=f'/question_images?quiz_id={quiz_id}&question_id={id}'
        )
    else:
        if form.validate_on_submit():
            if len(
                    list(
                        filter(
                            lambda f: f, [form.is_answer1.data, form.is_answer2.data,
                                          form.is_answer3.data, form.is_answer4.data]
                        )
                    )
            ) < 2:
                return render_template(
                    "question_setting.html",
                    mesage="Должно быть как минимум два ответа", form=form, quiz=quiz,
                    questions=ques, pic=f'/question_images?quiz_id={quiz_id}&question_id={id}'
                )

            question.question = form.question.data
            if form.is_answer1.data:
                question.answer1 = form.answer1_text.data
            else:
                question.answer1 = None
            if form.is_answer2.data:
                question.answer2 = form.answer2_text.data
            else:
                question.answer2 = None
            if form.is_answer3.data:
                question.answer3 = form.answer3_text.data
            else:
                question.answer3 = None
            if form.is_answer4.data:
                question.answer4 = form.answer4_text.data
            else:
                question.answer4 = None

            question.quiz_id = quiz_id
            question.true_answer = form.true_answer.data
            logging.debug("Добавление элемента в бд")
            db_sess.commit()

            if form.picture.validate(
                    form, extra_validators=[DataRequired()]
            ):
                f = Image.open(form.picture.data)
                f.thumbnail((1270, 720), Image.Resampling.LANCZOS)
                path = os.path.join(
                    app.instance_path,
                    'question_imgs',
                    f'quiz_{quiz_id}',
                    f"question_{question.id}.jpg"
                )
                f.save(path)
            logging.debug("Добавление элемента в бд")
            db_sess.commit()
            return redirect(f"/quizzes/redact/{quiz_id}/questions/{question.id}")

        return render_template(
            "question_setting.html", mesage="Должно быть как минимум два ответа",
            form=form, quiz=quiz, questions=ques,
            pic=f'/question_images?quiz_id={quiz_id}&question_id={id}'
        )


@app.route("/quizzes/delete/<int:id>")
def delete_quiz(id):
    if not current_user.is_authenticated:
        logging.warning("Пользователь не зарегистрирован")
        abort(404)
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).get(id)
    if not quiz or quiz.author_id != current_user.id:
        logging.warning("Пользователь {} не имеет прав на квиз {}".format(quiz.author_id, current_user.id))
        abort(404)
    if quiz.is_available == 0:
        href_reject = f"/quizzes/redact/{id}/settings"
    else:
        href_reject = f"/profile"
    href_aprove = f"/quizzes/delete/{id}/yes"

    return render_template("delete_quiz.html", hr=href_reject, ha=href_aprove, quiz=quiz)


@app.route("/quizzes/delete/<int:id>/yes")
def delete_quiz_yes(id):
    if not current_user.is_authenticated:
        logging.warning("Пользователь не зарегистрирован")
        abort(404)
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).get(id)
    if not quiz or quiz.author_id != current_user.id:
        abort(404)

    for q in db_sess.query(Question).filter(Question.quiz_id == id):
        logging.warning("Пользователь {} не имеет прав на квиз {}".format(quiz.author_id, current_user.id))
        db_sess.delete(q)

    for root, dirs, files in os.walk(os.path.join("instance", "question_imgs", f"quiz_{id}"), topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(os.path.join("instance", "question_imgs", f"quiz_{id}"))
    logging.debug("Удаление квиза {}".format(quiz.name))
    db_sess.delete(quiz)
    db_sess.commit()
    logging.debug("Удаление прошло")
    return redirect("/")


@app.route("/quizzes/publish/<int:id>")
def pub_quiz(id):
    if not current_user.is_authenticated:
        logging.warning("Пользователь не зарегистрирован")
        abort(404)
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).get(id)
    if not quiz or quiz.author_id != current_user.id:
        logging.warning("Пользователь {} не имеет прав на квиз {}".format(quiz.author_id, current_user.id))
        abort(404)

    if quiz.is_available:
        return redirect(f"/quizzes/published/{id}")

    href_reject = f"/quizzes/redact/{id}/settings"
    href_aprove = f"/quizzes/publish/{id}/yes"

    return render_template("quiz_publish.html", hr=href_reject, ha=href_aprove, quiz=quiz)


@app.route("/quizzes/publish/<int:id>/yes")
def pub_quiz_yes(id):
    if not current_user.is_authenticated:
        logging.warning("Пользователь не зарегистрирован")
        abort(404)
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).get(id)
    if not quiz or quiz.author_id != current_user.id:
        logging.warning("Пользователь {} не имеет прав на квиз {}".format(quiz.author_id, current_user.id))
        abort(404)

    if quiz.is_available:
        return redirect(f"/quizzes/published/{id}")

    quiz.is_available = True
    db_sess.commit()

    return redirect(f"/quizzes/published/{id}")


@app.route("/quizzes/published/<int:id>")
def published_dashboard(id):
    if not current_user.is_authenticated:
        logging.warning("Пользователь не зарегистрирован")
        abort(404)
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).get(id)
    if not quiz or quiz.author_id != current_user.id:
        logging.warning("Пользователь {} не имеет прав на квиз {}".format(quiz.author_id, current_user.id))
        abort(404)
    if not quiz.is_available:
        return redirect(f"/quizzes/redact/{id}/settings")

    return render_template("published_dashboard.html", quiz=quiz)


@app.route("/quizzes/play/<int:id>")
def play_quiz(id):
    if not current_user.is_authenticated:
        logging.warning("Пользователь не зарегистрирован")
        abort(404)
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).get(id)
    if not quiz.is_available:
        logging.warning("Квиз не опубликован")
        return abort(404)

    redirect = request.args.get("redirect", None)
    if redirect:
        href_reject = redirect
    else:
        href_reject = "/"
    href_aprove = f"/quizzes/play/{id}/yes"

    return render_template("quiz_play_q.html", hr=href_reject, ha=href_aprove, quiz=quiz)


@app.route("/quizzes/play/<int:id>/yes")
def play_quiz_yes(id):
    if not current_user.is_authenticated:
        logging.warning("Пользователь не зарегистрирован")
        abort(404)
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).get(id)
    if not quiz.is_available:
        logging.warning("Квиз не опубликован")
        return abort(404)

    qs = db_sess.query(Question).filter(Question.quiz_id == id)
    srcs = []
    questions = []
    answers = []
    for q in qs:
        srcs.append(f"/question_images?quiz_id={id}&question_id={q.id}")
        questions.append(q.question)
        answers.append(
            str(
                list(
                    filter(
                        lambda d: d is not None, [
                            q.answer1, q.answer2, q.answer3, q.answer4]
                    )
                )
            )
        )

    q_ctn = len(srcs)
    srcs = '"' + "\", \"".join(srcs) + '"'
    questions = '"' + "\", \"".join(questions) + '"'
    answers = ", ".join(answers)
    return render_template(
        "quiz_play.html", srcs=srcs,
        questions=questions, answers=answers, q_ctn=q_ctn, quiz=quiz
    )


@app.route("/quizzes/calculate/<int:id>", methods=["GET", "POST"])
def calc_result(id):
    db_sess = db_session.create_session()
    if not current_user.is_authenticated:
        abort(404)
    if request.method == 'GET':
        quiz = db_sess.query(Quiz).get(id)
        user = db_sess.query(User).get(current_user.id)
        if quiz in user.passages:
            return redirect(
                f'/quizzes/result/{id}?{"&".join(list([key + "=" + val for key, val in dict(request.args).items()]))}'
            )
        return render_template("calculate2.html")
    else:
        quiz = db_sess.query(Quiz).get(id)
        if not quiz.is_available:
            logging.warning("Квиз не опубликован")
            return abort(404)

        user = db_sess.query(User).get(current_user.id)
        if quiz not in user.passages:
            logging.debug("новое прохождение квиза {} пользователем {}".format(quiz.name, user.name))

            option = request.form['options']
            print(option)
            res_now = db_sess.query(Quiz).get(id)
            if res_now is None:
                res_now = 0
            print(res_now)
            count_now = len(
                db_sess.query(
                    association_table_passage
                ).filter_by(quizzes=id).all()
                )
            res_now.rating = (res_now.rating * count_now +
                              int(option)) / (count_now + 1)
            user.passages.append(quiz)
            db_sess.commit()
            logging.debug("Новое сохранение бд")
        else:
            logging.info("прохождение квиза {} пользователем {} уже совершалось".format(quiz.name, user.name))
        print(dict(request.args), 'args')
        return redirect(
            f'/quizzes/result/{id}?{"&".join(list([key + "=" + val for key, val in dict(request.args).items()]))}'
        )


@app.route('/quizzes/result/<int:id>')
def resultgame(id):
    if not current_user.is_authenticated:
        abort(404)
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).get(id)
    if not quiz.is_available:
        logging.warning("Квиз не опубликован")
        return abort(404)
    quistions = list()
    your_ans = list()
    right_ans = list()
    res = list()
    for i, q in enumerate(db_sess.query(Question).filter(Question.quiz_id == id).all()):
        quistions.append(q.question)
        your_ans.append(eval(f"q.answer{request.args.get(str(i))}"))
        right_ans.append(eval(f"q.answer{q.true_answer}"))
        ans = request.args.get(str(i))
        if ans is None:
            logging.warning("{} is none".format(i))
            abort(404)
        res.append(q.true_answer == int(ans))
    color = ["green" if element else "red" for element in res]
    res1 = [1 if element else 0 for element in res]
    return render_template(
        "calcres.html", name=quiz.name, items=zip(quistions, your_ans, right_ans, color, res1), count=res.count(True),
        lenquiz=len(res), theme=quiz.themes[0].name, id=quiz.id
    )


@login_manager.user_loader
def load_user(id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(id)


@app.route('/', methods=["GET", "POST"])
@app.route('/index', methods=["GET", "POST"])
@app.route('/menu', methods=["GET", "POST"])
def index():
    db_sess = db_session.create_session()
    if request.method == 'GET':
        monce = db_sess.query(Quiz).filter(
            Quiz.created_date.between(
                datetime.datetime.today().date() - datetime.timedelta(days=30),
                datetime.datetime.today().date() - datetime.timedelta(days=7)
            )
        ).order_by(desc(Quiz.rating)).all()
        week = db_sess.query(Quiz).filter(
            Quiz.created_date >=
            datetime.datetime.today().date() - datetime.timedelta(days=7)
        ).order_by(desc(Quiz.rating)).all()
        qpassage = db_sess.query(association_table_passage)
        monce = list(
            filter(
                lambda x: len(
                    qpassage.filter_by(quizzes=x.id).all()
                ) >= 2, monce
                )
            )
        week = list(
            filter(
                lambda x: len(
                    qpassage.filter_by(quizzes=x.id).all()
                ) >= 2, week
                )
            )

        monce1, monce2 = InfTempl(), InfTempl()
        week1, week2 = InfTempl(), InfTempl()

        if len(monce) >= 2:
            monce1.update(
                title=monce[0].name, theme=monce[0].themes[0].name, rating=round(monce[0].rating, 1), id=monce[0].id
            )
            monce2.update(
                title=monce[1].name, theme=monce[1].themes[0].name, rating=round(monce[1].rating, 1), id=monce[1].id
            )
        elif len(monce) == 1:
            monce1.update(
                title=monce[0].name, theme=monce[0].themes[0].name, rating=round(monce[0].rating, 1), id=monce[0].id
            )
        if len(week) >= 2:
            week1.update(
                title=week[0].name, theme=week[0].themes[0].name, rating=round(week[0].rating, 1), id=week[0].id
            )
            week2.update(
                title=week[1].name, theme=week[1].themes[0].name, rating=round(week[1].rating, 1), id=week[1].id
            )
        elif len(week) == 1:
            week1.update(
                title=week[0].name, theme=week[0].themes[0].name, rating=round(week[0].rating, 1), id=week[0].id
            )

        recommendation_main_theme, recommendation_random_theme, recommendation_random = InfTempl(
        ), InfTempl(), InfTempl()
        recommendation = list()
        if current_user.is_authenticated:
            complited = db_sess.query(association_table_passage).filter_by(
                users=current_user.id
            )
            if complited:
                complited_quizzes = list(map(lambda x: x.quizzes, complited))
                all_themes = [db_sess.query(Quiz).get(
                    id
                ).themes[0].name for id in complited_quizzes]
                for el in sorted(list(set(all_themes)), key=lambda x: all_themes.count(x), reverse=True):
                    res_list = list(
                        filter(
                            lambda x: x.themes[0].name == el and x.id not in complited_quizzes,
                            db_sess.query(Quiz).all()
                        )
                    )
                    if res_list:
                        result = choice(res_list)
                        recommendation_main_theme.update(
                            title=result.name, theme=result.themes[0].name, rating=round(result.rating, 1), id=result.id
                        )
                        recommendation.append(result.id)
                        break
                for el in sample(all_themes, len(all_themes)):
                    res_list = list(
                        filter(
                            lambda x: x.themes[
                                          0].name == el and x.id not in complited_quizzes and x.id not in recommendation,
                            db_sess.query(Quiz).all()
                        )
                    )
                    if res_list:
                        result = choice(res_list)
                        recommendation_random_theme.update(
                            title=result.name, theme=result.themes[0].name
                        )
                        recommendation.append(result.id)
                        break
                res_list1 = list(
                    filter(
                        lambda x: x.id not in complited_quizzes and x.id not in recommendation,
                        db_sess.query(Quiz).all()
                    )
                )
                if res_list1:
                    res1 = choice(res_list1)
                    recommendation_random.update(
                        title=res1.name, theme=res1.themes[0].name
                    )
                    recommendation.append(res1.id)
        else:
            logging.warning("Пользователь не зарегистрирован")
        logging.info(
            '{} {}'.format(
                recommendation_main_theme.title,
                recommendation_random_theme.title, recommendation_random.title
                )
            )
        logging.info(
            '{} {} {} {}'.format(
                recommendation_main_theme.title,
                recommendation_main_theme.theme,
                [recommendation_random_theme.title, recommendation_random.title],
                [recommendation_random_theme.theme, recommendation_random.theme]
            )
        )
        logging.info('{} {} {} {}'.format(monce1.title, monce2.title, week1.title, week2.title))
        rec_list = [(recommendation_random_theme.title, recommendation_random_theme.theme),
                    (recommendation_random.title, recommendation_random.theme)]
        return render_template(
            "index.html", monce_name1=monce1.title, monce_name2=monce2.title, week_name1=week1.title,
            week_name2=week2.title, monce_theme1=monce1.theme, monce_theme2=monce2.theme, week_theme1=week1.theme,
            week_theme2=week2.theme, rec_name=recommendation_main_theme.title,
            rec_theme=recommendation_main_theme.theme,
            monce_rating1=monce1.rating, monce_rating2=monce2.rating, week_rating1=week1.rating,
            week_rating2=week2.rating, monce_id1=monce1.id, monce_id2=monce2.id, week_id1=week1.id, week_id2=week2.id,
            rec_id=recommendation_main_theme.id

        )
    if request.method == 'POST':
        code = request.form['code']
        if code.isdigit():
            quiz = db_sess.query(Quiz).get(code)
            if not quiz:
                abort(404)
            return redirect(f'/quizzes/play/{code}')
        else:
            return redirect(f'/search/{code}')


@app.route("/profile")
def profile():
    if not current_user.is_authenticated:
        logging.warning("Пользователь не зарегистрирован")
        return redirect(f"/login")
    db_sess = db_session.create_session()

    qs = list(
        filter(
            lambda x: x.author.id ==
                      current_user.id, db_sess.query(Quiz)
            )
        )
    complited = list(
        filter(
            lambda x: x.users == current_user.id,
            db_sess.query(association_table_passage)
            )
        )
    return render_template("profile.html", myquizzes=qs, lenqs=len(qs), lencomplited=len(complited))


@app.route('/search/<string:code>', methods=["GET", "POST"])
def search(code):
    db_sess = db_session.create_session()
    if request.method == 'GET':
        seleceter = list(
            filter(
                lambda x: code.lower() in x.name.lower(),
                db_sess.query(Quiz).filter(Quiz.is_available == 1).all()
                )
        )
        return render_template("search.html", quizzeshere=seleceter)
    else:
        code = request.form['code_searcher']
        if code.isdigit():
            quiz = db_sess.query(Quiz).get(code)
            if not quiz:
                abort(404)
            return redirect(f'/quizzes/play/{code}')
        else:
            return redirect(f'/search/{code}')


@app.route("/about")
def about():
    r = requests.get("https://api.github.com/repos/CHERTvsINTERNET/webporject")
    if not r:
        stars = "??"
    else:
        stars = r.json()["stargazers_count"]
    r = requests.get(
        "https://api.github.com/repos/CHERTvsINTERNET/webporject/contributors"
    )
    if not r:
        contrebutors = []
    contrebutors = []
    for c in r.json():
        contrebutors.append(
            {
                'image': c["avatar_url"],
                "name": c['login'],
                'url': c["html_url"]
            }
        )
    return render_template("about.html", contrebutors=contrebutors, stars=stars)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")




if __name__ == "__main__":
    logging.info("Начало выполнения")
    main()
    app.run(host="127.0.0.1", port=8080)
