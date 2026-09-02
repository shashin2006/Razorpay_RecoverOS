from fastapi import FastAPI,Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.database import Base, engine, get_db
from app.db import models
from app.api.webhooks import router as webhook_router
from fastapi.responses import FileResponse
from app.api.ml import router as ml_router
from app.core.logging_config import configure_logging
from app.api.agent import router as agent_router
from app.api.recovery_agent import router as rec_agent_router
from fastapi.middleware.cors import CORSMiddleware
from app.api.recovery import router as recovery_router

Base.metadata.create_all(bind=engine)

configure_logging()

app = FastAPI(title="RecoveryOS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook_router)
app.include_router(ml_router)
app.include_router(agent_router)
app.include_router(rec_agent_router)
app.include_router(recovery_router)

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