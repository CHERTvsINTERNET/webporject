import sqlalchemy as sa
from .db_session import SqlAlchemyBase

association_table_passage = sa.Table(
    'association_passage',
    SqlAlchemyBase.metadata,
    sa.Column(
        'id',
        sa.Integer, primary_key=True,
        autoincrement=True
        ),
    sa.Column(
        'users', sa.Integer,
        sa.ForeignKey('users.id')
        ),
    sa.Column(
        'quizzes', sa.Integer,
        sa.ForeignKey('quizzes.id')
        )
)
