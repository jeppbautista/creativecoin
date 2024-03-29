"""empty message

Revision ID: 616f80b9c007
Revises: 19197b00fbd9
Create Date: 2020-07-01 12:40:49.492997

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '616f80b9c007'
down_revision = '19197b00fbd9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('payment', sa.Column('status', sa.String(length=128), nullable=True))
    op.create_foreign_key(None, 'payment', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'transaction', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'wallet', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'wallet', type_='foreignkey')
    op.drop_constraint(None, 'transaction', type_='foreignkey')
    op.drop_constraint(None, 'payment', type_='foreignkey')
    op.drop_column('payment', 'status')
    # ### end Alembic commands ###
