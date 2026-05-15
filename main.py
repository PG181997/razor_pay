from fastapi import FastAPI
from routes import tenants

app = FastAPI(title="razor pay")
app.include_router(tenants.router)
