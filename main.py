import os
import datetime
from flask import Flask, abort, redirect, render_template, request, send_file, url_for
from flask_login import LoginManager, current_user, login_user, logout_user
from PIL import Image
from sqlalchemy import desc
from wtforms.validators import DataRequired

from blueprints import question_image_getter
from data import db_session
from data.questions import Question
from data.quizzes import Quiz
from data.themes import Theme
from data.user import User
from forms.question import QuestionAdd, QuestionRedact
from forms.quiz import QuizAddForm, QuizSettingsForm
from forms.user import UserLoginForm, UserRegisterForm

from objects.information_template import InfTempl
import fuckit

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
        abort(404)

    form = UserLoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()

        user = db_sess.query(User).filter(
            User.email == form.email.data
        ).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        form.password.data = ""
        return render_template(
            "login.html", message="Неверное email или пароль",
            form=form, title="Авторизация"
        )
    return render_template("login.html", form=form, title="Авторизация")


@app.route("/register", methods=["GET", "POST"])
def register_page():
    if current_user.is_authenticated:
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
        abort(404)

    form = QuizAddForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        quiz = Quiz()
        quiz.name = form.quiz_name.data
        quiz.description = form.quiz_description.data
        quiz.author_id = current_user.id
        db_sess.add(quiz)
        db_sess.commit()
        os.makedirs(
            os.path.join(
                app.instance_path,
                'question_imgs', f'quiz_{quiz.id}'
            )
        )

        return redirect(f"/quizzes/redact/{quiz.id}/settings")

    return render_template("quiz_pre_redact.html", title="Создание квиза", form=form)


@app.route("/quizzes/redact/<int:id>/settings", methods=["GET", "POST"])
def redact_quiz_settings(id):
    if not current_user.is_authenticated:
        abort(404)
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).get(id)
    if not quiz or quiz.author_id != current_user.id:
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
        abort(404)
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).get(quiz_id)
    if not quiz or quiz.author_id != current_user.id:
        abort(404)
    if quiz.is_available:
        return redirect(f"/quizzes/published/{id}")

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
                message="Должно быть как минимум два вопроса", form=form, quiz=quiz, questions=ques
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
        abort(404)
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).get(quiz_id)
    if not quiz or quiz.author_id != current_user.id:
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
                    mesage="Должно быть как минимум два вопроса", form=form, quiz=quiz,
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
            db_sess.commit()
            return redirect(f"/quizzes/redact/{quiz_id}/questions/{question.id}")

        return render_template(
            "question_setting.html", mesage="Должно быть как минимум два вопроса",
            form=form, quiz=quiz, questions=ques,
            pic=f'/question_images?quiz_id={quiz_id}&question_id={id}'
        )


@app.route("/quizzes/delete/<int:id>")
def delete_quiz(id):
    if not current_user.is_authenticated:
        abort(404)
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).get(id)
    if not quiz or quiz.author_id != current_user.id:
        abort(404)

    href_reject = f"/quizzes/redact/{id}/settings"
    href_aprove = f"/quizzes/delete/{id}/yes"

    return render_template("delete_quiz.html", hr=href_reject, ha=href_aprove, quiz=quiz)


@app.route("/quizzes/delete/<int:id>/yes")
def delete_quiz_yes(id):
    if not current_user.is_authenticated:
        abort(404)
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).get(id)
    if not quiz or quiz.author_id != current_user.id:
        abort(404)

    for q in db_sess.query(Question).filter(Question.quiz_id == id):
        db_sess.delete(q)

    for root, dirs, files in os.walk(os.path.join("instance", "question_imgs", f"quiz_{id}"), topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(os.path.join("instance", "question_imgs", f"quiz_{id}"))

    db_sess.delete(quiz)
    db_sess.commit()

    return redirect("/")


@app.route("/quizzes/publish/<int:id>")
def pub_quiz(id):
    if not current_user.is_authenticated:
        abort(404)
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).get(id)
    if not quiz or quiz.author_id != current_user.id:
        abort(404)

    if quiz.is_available:
        return redirect(f"/quizzes/published/{id}")

    href_reject = f"/quizzes/redact/{id}/settings"
    href_aprove = f"/quizzes/publish/{id}/yes"

    return render_template("quiz_publish.html", hr=href_reject, ha=href_aprove, quiz=quiz)


@app.route("/quizzes/publish/<int:id>/yes")
def pub_quiz_yes(id):
    if not current_user.is_authenticated:
        abort(404)
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).get(id)
    if not quiz or quiz.author_id != current_user.id:
        abort(404)

    if quiz.is_available:
        return redirect(f"/quizzes/published/{id}")

    quiz.is_available = True
    db_sess.commit()

    return redirect(f"/quizzes/published/{id}")


@app.route("/quizzes/published/<int:id>")
def published_dashboard(id):
    if not current_user.is_authenticated:
        abort(404)
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).get(id)
    if not quiz or quiz.author_id != current_user.id:
        abort(404)
    if not quiz.is_available:
        return redirect(f"/quizzes/redact/{id}/settings")

    return render_template("published_dashboard.html", quiz=quiz)


@app.route("/quizzes/play/<int:id>")
def play_quiz(id):
    if not current_user.is_authenticated:
        abort(404)
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).get(id)
    if not quiz.is_available:
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
        abort(404)
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).get(id)
    if not quiz.is_available:
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


@app.route("/quizzes/calculate/<int:id>")
def calc_result(id):
    if not current_user.is_authenticated:
        abort(404)
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).get(id)
    if not quiz.is_available:
        return abort(404)

    results = []
    for i, q in enumerate(db_sess.query(Question).filter(Question.quiz_id == id).all()):
        ans = request.args.get(str(i))
        if ans is None:
            print(i, "is none")
            abort(404)

        results.append(q.true_answer == int(ans))

    user = db_sess.query(User).get(current_user.id)
    if quiz not in user.passages:
        print("новый")
        user.passages.append(quiz)
        db_sess.commit()
    else:
        print("Уже был")

    return render_template("calc_results.html", results=results, quiz=quiz)


@login_manager.user_loader
def load_user(id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(id)


@app.route('/', methods=["GET", "POST"])
@app.route('/index', methods=["GET", "POST"])
@app.route('/menu', methods=["GET", "POST"])
def index():
    global monce1, monce2, week1, week2
    db_sess = db_session.create_session()
    if request.method == 'GET':
        print()
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
        monce1, monce2 = InfTempl(), InfTempl()
        week1, week2 = InfTempl(), InfTempl()
        print(week[0].name)
        themes = db_sess.query(Theme).get(week[0].themeinquiz).name
        print(themes)

        @fuckit
        def updateinf(monce, week, db_sess):
            monce1.update(title=monce[0].name, theme=db_sess.query(Theme).get(monce[0].themeinquiz).name)
            monce2.update(title=monce[1].name, theme=db_sess.query(Theme).get(monce[1].themeinquiz).name)
            week1.update(title=week[0].name, theme=db_sess.query(Theme).get(week[0].themeinquiz).name)
            week2.update(title=week[1].name, theme=db_sess.query(Theme).get(week[1].themeinquiz).name)

        updateinf(monce, week, db_sess)
        print(monce1.title, monce2.title, week1.title, week2.title)
        return render_template(
            "index.html", monce_name1=monce1.title, monce_name2=monce2.title, week_name1=week1.title,
            week_name2=week2.title, monce_theme1=monce1.theme, monce_theme2=monce2.theme, week_theme1=week1.theme,
            week_theme2=week2.theme
        )
    if request.method == 'POST':
        code = request.form['code']
        quiz = db_sess.query(Quiz).get(code)
        if not quiz:
            abort(404)
        return redirect(f'/quizzes/play/{code}')


if __name__ == "__main__":
    main()
    app.run(host="127.0.0.1", port=8080)
