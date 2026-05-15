from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from passlib.context import CryptContext
import logging
from sqlalchemy.exc import IntegrityError
from database import get_db

router = APIRouter(prefix="/users", tags=["users"])
bcrypt_context = CryptContext(schemes=["bcrypt"])


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    tenent_id: int


@router.post("/", status_code=201)
async def create_user(users: UserCreate, db: AsyncSession = Depends(get_db)):

    new_user = User(
        username=users.username,
        email=users.email,
        hashed_password=bcrypt_context.hash(users.password),
        tenant_id=users.tenent_id,
    )

    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return {
            "id": new_user.id,
            "name": new_user.username,
            "email": new_user.email,
            "created at": new_user.created_at,
            "updated at": new_user.updated_at,
            "tenant id": new_user.tenant_id,
        }
    except IntegrityError as e:
        logging.exception(e)
        await db.rollback()

        if "ForeignKeyViolation" in str(e):
            raise HTTPException(status_code=404, detail="Tenant id not found.")
        else:
            raise HTTPException(status_code=409, detail="email conflict.")

    except Exception as e:
        logging.exception(e)
        await db.rollback()
        raise
