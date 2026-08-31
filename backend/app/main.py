from fastapi import FastAPI,Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.database import Base, engine, get_db
from app.db import models
from app.api.webhooks import router as webhook_router
from fastapi.responses import FileResponse
from app.api.ml import router as ml_router
from app.core.logging_config import configure_logging

Base.metadata.create_all(bind=engine)

configure_logging()

app = FastAPI(title="RecoveryOS")

app.include_router(webhook_router)
app.include_router(ml_router)

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "recovery-os",
    }

@app.get("/health/db")
async def database_health(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "database": result.scalar(),
    }

@app.get("/test-checkout")
async def test_checkout():
    return FileResponse("test_checkout.html")