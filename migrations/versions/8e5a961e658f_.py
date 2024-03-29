"""empty message

Revision ID: 8e5a961e658f
Revises: 4d467e0553f1
Create Date: 2020-06-28 18:35:25.320911

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '8e5a961e658f'
down_revision = '4d467e0553f1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('transaction', sa.Column('user_id', sa.String(length=128), nullable=True))
    op.create_foreign_key(None, 'transaction', 'user', ['user_id'], ['email'], ondelete='CASCADE')
    op.drop_column('transaction', 'email')
    op.create_foreign_key(None, 'wallet', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'wallet', type_='foreignkey')
    op.add_column('transaction', sa.Column('email', mysql.VARCHAR(length=128), nullable=True))
    op.drop_constraint(None, 'transaction', type_='foreignkey')
    op.drop_column('transaction', 'user_id')
    # ### end Alembic commands ###
