from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models.tenant import Tenant
import logging
from sqlalchemy.exc import IntegrityError

from routes.auth import get_current_user

router = APIRouter(prefix="/tenants", tags=["tenants"])


class TenantCreate(BaseModel):
    name: str
    api_key: str


@router.post("/", status_code=201, dependencies=[Depends(get_current_user)])
async def tenant_create(tenant: TenantCreate, db: AsyncSession = Depends(get_db)):

    new_tenant = Tenant(name=tenant.name, api_key=tenant.api_key)

    try:
        db.add(new_tenant)
        await db.commit()
        await db.refresh(new_tenant)
        return {
            "id": new_tenant.id,
            "api_key": new_tenant.api_key,
            "name": new_tenant.name,
            "created_at": new_tenant.created_at,
            "updated_at": new_tenant.updated_at,
        }
    except IntegrityError as e:
        logging.exception(e)
        await db.rollback()
        raise HTTPException(status_code=409, detail="api key conflict")

    except Exception as e:
        logging.exception(e)
        await db.rollback()
        raise
