import os

from flask import Flask, abort, redirect, render_template, request, send_file
from flask_login import LoginManager, current_user, login_user, logout_user

from data import db_session
from data.questions import Question
from data.quizzes import Quiz
from data.user import User
from forms.quiz import QuizAddForm, QuizSettingsForm
from forms.user import UserLoginForm, UserRegisterForm

app = Flask(__file__)
app.config['SECRET_KEY'] = 'mega-slohni-sekret-key-voobshe-nikto-ne-dogadaetsa'

login_manager = LoginManager()
login_manager.init_app(app)


def main():
    if not "db" in os.listdir(".") or not os.path.isdir("db"):
        os.makedirs("db")
    db_session.global_init("./db/blob.db")


@app.route("/login", methods=["GET", "POST"])
def login_page():
    if current_user.is_authenticated:
        abort(404)

    form = UserLoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()

        user = db_sess.query(User).filter(
            User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        form.password.data = ""
        return render_template("login.html", message="Неверное email или пароль", form=form, title="Авторизация")
    return render_template("login.html", form=form, title="Авторизация")


@app.route("/register", methods=["GET", "POST"])
def register_page():
    if current_user.is_authenticated:
        abort(404)

    form = UserRegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template("register.html", form=form, title="Регистрация", message="Пароли не совпадают", current_user=current_user)
        db_sess = db_session.create_session()
        # если почта ужесуществует
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template("register.html", form=form, title="Регистрация", message="Такая почта уже зарегистрированна", current_user=current_user)
        user = User()
        user.name = form.name.data
        user.email = form.email.data
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect("/login")
    return render_template("register.html", form=form, title="Регистрация", current_user=current_user)


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
        return redirect(f"/quizzes/redact/{quiz.id}/settings")

    return render_template("quiz_pre_redact.html", title="Создание квиза", form=form)


@app.route("/quizzes/redact/<int:id>/settings", methods=["GET", "POST"])
def redact_quiz_settings(id):
    if not current_user.is_authenticated:
        abort(404)
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).get(id)
    if quiz.author_id != current_user.id:
        abort(404)

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
    return render_template("quiz_settings.html", form=form, title='Настройки квиза', questions=ques, quiz=quiz)


@login_manager.user_loader
def load_user(id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(id)


if __name__ == "__main__":
    main()
    app.run(host="127.0.0.1", port=8080)
