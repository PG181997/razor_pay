from models.user import User
from sqlalchemy import select
from pydantic import BaseModel
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, APIRouter, HTTPException
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

load_dotenv()
oauth2_bearer = HTTPBearer()
KEY = os.getenv("SECRET_KEY")

router = APIRouter(prefix="/login", tags=["login"])
bcrypt_context = CryptContext(schemes=["bcrypt"])


class Login(BaseModel):
    email: str
    password: str


def generate_token(user_id: int, user_email: str, tenant_id: int):
    data = {"id": user_id, "email": user_email, "tenantid": tenant_id}
    exp = datetime.utcnow() + timedelta(minutes=30)
    data["exp"] = exp
    token = jwt.encode(data, KEY, "HS256")
    return token


@router.post("/", status_code=200)
async def login_user(login: Login, db: AsyncSession = Depends(get_db)):

    response = await db.execute(select(User).where(User.email == login.email))
    db_user = response.scalar_one_or_none()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")

    is_auth = bcrypt_context.verify(login.password, db_user.hashed_password)

    if not is_auth:
        raise HTTPException(status_code=401, detail="password not correct")

    return generate_token(db_user.id, db_user.email, db_user.tenant_id)


async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(oauth2_bearer),
):
    try:
        payload = jwt.decode(token.credentials, KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="jwt decode failed")
