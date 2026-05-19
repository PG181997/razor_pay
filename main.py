from fastapi import FastAPI
from routes import auth, tenants, users, wallets, payments
from contextlib import asynccontextmanager
from arq.connections import create_pool, RedisSettings


@asynccontextmanager
async def lifespane(app):
    app.state.redis = await create_pool(RedisSettings(host="localhost", port=6379))
    yield
    await app.state.redis.close()


app = FastAPI(title="razor pay", lifespan=lifespane)
app.include_router(tenants.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(wallets.router)
app.include_router(payments.router)
