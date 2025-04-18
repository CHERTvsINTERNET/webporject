from datetime import datetime
import sqlalchemy as sa
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Quizzes(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'quizzes'

    id = sa.Column(
        sa.Integer, primary_key=True, autoincrement=True
    )
    name = sa.Column(sa.String, nullable=False, unique=True)
    description = sa.Column(sa.String)
    author = sa.Column(sa.Integer, sa.ForeignKey("users.id"))
    created_date = sa.Column(
        sa.DateTime,
        default=datetime.now
    )
    rating = sa.Column(sa.Float)
    reward = sa.Column(sa.Integer)  # Зачем??
