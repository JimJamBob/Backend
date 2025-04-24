"""setup user table

Revision ID: de0e71a678c9
Revises: 68774871b0eb
Create Date: 2025-04-24 12:13:06.207712

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'de0e71a678c9'
down_revision: Union[str, None] = '68774871b0eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table("users", 
                    sa.Column("email", sa.String, nullable = False), 
                    sa.Column("password", sa.String, nullable = False), 
                    sa.Column("id", sa.Integer, nullable = False), 
                    sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable = False, server_default = sa.text('now()')),
                    sa.PrimaryKeyConstraint("id"),
                    sa.UniqueConstraint("email")                                        
                    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("users")
    pass
