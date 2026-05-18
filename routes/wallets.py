from fastapi import APIRouter, Depends, HTTPException
from routes.auth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models.wallet import Wallet
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/wallets", tags=["wallets"])

@router.post("/", status_code=201)
async def wallet_create(db:AsyncSession = Depends(get_db), current_user:dict = Depends(get_current_user)):

    try:
        new_wallet = Wallet(user_id = current_user["id"])
        db.add(new_wallet)
        await db.commit()
        await db.refresh(new_wallet)
        return {"response":{"id":new_wallet.id, "user_id":new_wallet.user_id}}
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Failed to create wallet.")
