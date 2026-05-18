from fastapi import FastAPI
from routes import auth, tenants, users, wallets, payments

app = FastAPI(title="razor pay")
app.include_router(tenants.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(wallets.router)
app.include_router(payments.router)
