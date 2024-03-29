"""empty message

Revision ID: 7e0d68c87ec1
Revises: 786027637b20
Create Date: 2020-07-01 12:46:31.032933

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7e0d68c87ec1'
down_revision = '786027637b20'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'payment', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'transaction', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'wallet', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'wallet', type_='foreignkey')
    op.drop_constraint(None, 'transaction', type_='foreignkey')
    op.drop_constraint(None, 'payment', type_='foreignkey')
    # ### end Alembic commands ###
