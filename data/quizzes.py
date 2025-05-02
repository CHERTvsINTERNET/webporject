from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Quiz(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'quizzes'

    id = sa.Column(
        sa.Integer, primary_key=True, autoincrement=True
    )
    name = sa.Column(sa.String, nullable=False, unique=True)
    description = sa.Column(sa.String)
    author_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))
    created_date = sa.Column(
        sa.Date,
        default=datetime.now().date
    )
    rating = sa.Column(sa.Float)
    reward = sa.Column(sa.Integer)  # Зачем??
    is_available = sa.Column(sa.Boolean, default=False)

    author = orm.relationship("User", foreign_keys=[author_id])
    themes = orm.relationship(
        "Theme", secondary="association_theme", backref="quizzes")
