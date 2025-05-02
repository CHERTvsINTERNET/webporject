import sqlalchemy
from sqlalchemy.util.preloaded import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class AssociationTheme(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'association_theme'

    id = sqlalchemy.Column(
        sqlalchemy.Integer, primary_key=True, autoincrement=True
    )
    quiz = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey('quizzes.id'), nullable=False
    )
    theme = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey('themes.id'), nullable=False
    )
