import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Question(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'questions'

    id = sa.Column(
        sa.Integer, primary_key=True, autoincrement=True
    )
    question = sa.Column(sa.String, nullable=False)

    image = sa.Column(sa.String)

    answer1 = sa.Column(sa.String, nullable=False)
    answer2 = sa.Column(sa.String, nullable=False)
    answer3 = sa.Column(sa.String)
    answer4 = sa.Column(sa.String)

    quiz_id = sa.Column(sa.Integer, sa.ForeignKey("quizzes.id"))

    quiz = orm.relationship("Quiz")
