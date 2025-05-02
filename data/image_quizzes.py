import sqlalchemy as sa

from .db_session import SqlAlchemyBase

association_table_img = sa.Table(
    'association_image_quizzes',
    SqlAlchemyBase.metadata,
    sa.Column(
        'id',
        sa.Integer, primary_key=True,
        autoincrement=True
    ),
    sa.Column(
        'quizzes', sa.Integer,
        sa.ForeignKey('quizzes.id')
    ),
    sa.Column(
        'src', sa.String,
    )
)
