"""add language to posts

Revision ID: 286eb5950a46
Revises: 51cb376c3e3a
Create Date: 2021-02-25 09:29:58.681470

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '286eb5950a46'
down_revision = '51cb376c3e3a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('post', sa.Column('language', sa.String(length=5), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('post', 'language')
    # ### end Alembic commands ###