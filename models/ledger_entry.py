from sqlalchemy import ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column
from database import Base
import enum


class EnteryType(enum.Enum):
    debit = "debit"
    credit = "credit"


class LedgerEntry(Base):
    __tablename__ = "ledgerentry"
    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[int] = mapped_column()
    type: Mapped[EnteryType] = mapped_column(Enum(EnteryType))
    transation_id: Mapped[int] = mapped_column(ForeignKey("transactions.id"))
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallets.id"))
