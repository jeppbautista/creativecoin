"""empty message

Revision ID: c2839a92d5a0
Revises: 7e0d68c87ec1
Create Date: 2020-07-01 15:03:02.604649

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c2839a92d5a0'
down_revision = '7e0d68c87ec1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('payment', sa.Column('updated', sa.TIMESTAMP(timezone=True), nullable=True))
    op.create_foreign_key(None, 'payment', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'transaction', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'wallet', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'wallet', type_='foreignkey')
    op.drop_constraint(None, 'transaction', type_='foreignkey')
    op.drop_constraint(None, 'payment', type_='foreignkey')
    op.drop_column('payment', 'updated')
    # ### end Alembic commands ###
