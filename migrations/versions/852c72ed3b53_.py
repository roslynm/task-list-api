"""empty message

Revision ID: 852c72ed3b53
Revises: bdefba3c6019
Create Date: 2021-10-28 11:02:35.556740

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '852c72ed3b53'
down_revision = 'bdefba3c6019'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('task', sa.Column('is_complete', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('task', 'is_complete')
    # ### end Alembic commands ###