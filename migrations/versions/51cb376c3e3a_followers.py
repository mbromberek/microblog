"""followers

Revision ID: 51cb376c3e3a
Revises: 7cb51fe8770d
Create Date: 2021-02-20 15:34:30.267341

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '51cb376c3e3a'
down_revision = '7cb51fe8770d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('followers',
    sa.Column('follower_id', sa.Integer(), nullable=True),
    sa.Column('followed_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['followed_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['follower_id'], ['user.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('followers')
    # ### end Alembic commands ###