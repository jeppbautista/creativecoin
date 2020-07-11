"""empty message

Revision ID: a08638248a8e
Revises: b02c7cf0ceff
Create Date: 2020-05-23 10:58:30.994993

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a08638248a8e'
down_revision = 'b02c7cf0ceff'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('firstname', sa.String(length=128), nullable=True))
    op.add_column('user', sa.Column('lastname', sa.String(length=128), nullable=True))
    op.add_column('user', sa.Column('phonenumber', sa.String(length=20), nullable=True))
    op.drop_column('user', 'last_name')
    op.drop_column('user', 'phone_number')
    op.drop_column('user', 'first_name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('first_name', mysql.VARCHAR(length=128), nullable=True))
    op.add_column('user', sa.Column('phone_number', mysql.VARCHAR(length=20), nullable=True))
    op.add_column('user', sa.Column('last_name', mysql.VARCHAR(length=128), nullable=True))
    op.drop_column('user', 'phonenumber')
    op.drop_column('user', 'lastname')
    op.drop_column('user', 'firstname')
    # ### end Alembic commands ###