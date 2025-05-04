from flask import Blueprint, jsonify, make_response, request, send_file

from data import db_session
from data.questions import Question
from data.quizzes import Quiz

question_image_getter = Blueprint(
    'question_image_getter',
    __name__,
    template_folder='templates'
)


@question_image_getter.route("/question_images")
def get_image():
    quiz_id = request.args["quiz_id"]
    if quiz_id is None or not quiz_id.isnumeric():
        return make_response(jsonify({'error': 'Bad request'}), 400)

    question_id = request.args["question_id"]
    if question_id is None or not question_id.isnumeric():
        return make_response(jsonify({'error': 'Bad request'}), 400)

    db_sess = db_session.create_session()
    question = db_sess.query(Question).filter(
        Question.quiz_id == quiz_id, Question.id == question_id).first()

    if not question:
        return make_response(jsonify({'error': 'Not found'}), 404)

    return send_file(f"instance/question_imgs/quiz_{quiz_id}/question_{question_id}.jpg")


@question_image_getter.route("/quiz_cover")
def get_quiz_cover():
    quiz_id = request.args["quiz_id"]
    if quiz_id is None or not quiz_id.isnumeric():
        return make_response(jsonify({'error': 'Bad request'}), 400)

    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).filter(Quiz.id == quiz_id).first()

    if not quiz:
        return make_response(jsonify({'error': 'Not found'}), 404)

    return send_file(f"instance/question_imgs/quiz_{quiz_id}/cover.jpg")
