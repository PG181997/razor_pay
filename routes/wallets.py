from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from routes.auth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models.wallet import Wallet
from models.topup import Topup
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

router = APIRouter(prefix="/wallets", tags=["wallets"])


class Wallet_topup(BaseModel):
    amount: int
    idempotency: str


@router.post("/", status_code=201)
async def wallet_create(
    db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)
):

    try:
        new_wallet = Wallet(user_id=current_user["id"])
        db.add(new_wallet)
        await db.commit()
        await db.refresh(new_wallet)
        return {"response": {"id": new_wallet.id, "user_id": new_wallet.user_id}}
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Failed to create wallet.")


@router.patch("/{wallet_id}", status_code=200)
async def wallet_topup(
    wallet_topup: Wallet_topup,
    wallet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):

    wallet_result = await db.execute(select(Wallet).where(Wallet.id == wallet_id))
    wallet_obj = wallet_result.scalar_one_or_none()

    idempotency_result = await db.execute(
        select(Topup).where(Topup.idempotency_key == wallet_topup.idempotency)
    )
    idempotency_obj = idempotency_result.scalar_one_or_none()

    if not wallet_obj:
        raise HTTPException(status_code=400, detail="Wallet not found")

    if idempotency_obj:
        return {
            "amount added": idempotency_obj.amount,
            "Total wallet balance": wallet_obj.balance,
        }

    if wallet_obj.user_id != current_user.get("id"):
        raise HTTPException(status_code=403, detail="authentication failed")

    wallet_obj.balance += wallet_topup.amount

    try:
        topup_record = Topup(
            wallet_id=wallet_id,
            amount=wallet_topup.amount,
            idempotency_key=wallet_topup.idempotency,
        )
        db.add(topup_record)
        db.add(wallet_obj)
        await db.commit()
        await db.refresh(topup_record)
        return {
            "amount added": wallet_topup.amount,
            "Total wallet balance": wallet_obj.balance,
        }

    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Failed balance update.")
