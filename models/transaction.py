from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from database import Base
from datetime import datetime


class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    from_wallet_id: Mapped[int] = mapped_column(ForeignKey("wallets.id"))
    to_wallet_id: Mapped[int] = mapped_column(ForeignKey("wallets.id"))
    idempotecy_key: Mapped[str] = mapped_column(unique=True)
