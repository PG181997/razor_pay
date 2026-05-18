from pydantic import BaseModel
from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from routes.auth import get_current_user
from sqlalchemy import select
from models.wallet import Wallet
from models.ledger_entry import LedgerEntry, EnteryType
from models.transaction import Transaction
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/payments", tags=["payments"])


class Payments(BaseModel):
    from_wallet_id: int
    to_wallet_id: int
    amount: int
    idempotency: str


@router.post("/", status_code=201)
async def create_payment(
    payment: Payments,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    from_wallet_result = await db.execute(
        select(Wallet).where(Wallet.id == payment.from_wallet_id)
    )
    from_wallet = from_wallet_result.scalar_one_or_none()

    if not from_wallet:
        raise HTTPException(status_code=404, detail="From wallet not found.")

    to_wallet_result = await db.execute(
        select(Wallet).where(Wallet.id == payment.to_wallet_id)
    )
    to_wallet = to_wallet_result.scalar_one_or_none()

    if from_wallet.user_id != current_user.get("id"):
        raise HTTPException(
            status_code=403, detail="From account does not mach the loggedin user"
        )

    if not to_wallet:
        raise HTTPException(status_code=404, detail="To user not found.")

    if payment.amount > from_wallet.balance:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    try:
        transaction = Transaction(
            from_wallet_id=from_wallet.id,
            to_wallet_id=to_wallet.id,
            idempotecy_key=payment.idempotency,
            amount=payment.amount,
        )

        db.add(transaction)
        await db.flush()

        from_wallet_ledger_entery = LedgerEntry(
            amount=payment.amount,
            type=EnteryType.debit,
            wallet_id=from_wallet.id,
            transation_id=transaction.id,
        )
        to_wallet_ledger_entery = LedgerEntry(
            amount=payment.amount,
            type=EnteryType.credit,
            wallet_id=to_wallet.id,
            transation_id=transaction.id,
        )

        from_wallet.balance -= payment.amount
        to_wallet.balance += payment.amount

        db.add(from_wallet_ledger_entery)
        db.add(to_wallet_ledger_entery)
        await db.commit()
        await db.refresh(to_wallet_ledger_entery)
        await db.refresh(from_wallet_ledger_entery)

        return {"transation_id": transaction.id, "balance": from_wallet.balance}
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Failed payment")
