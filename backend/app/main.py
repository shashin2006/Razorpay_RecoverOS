from fastapi import FastAPI, Depends, Request
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

import razorpay
from pathlib import Path

from app.db.database import Base, engine, get_db
from app.db import models
from app.api.webhooks import router as webhook_router
from app.api.ml import router as ml_router
from app.core.logging_config import configure_logging
from app.core.config import settings
from app.api.agent import router as agent_router
from app.api.recovery_agent import router as rec_agent_router
from app.api.recovery import router as recovery_router
Base.metadata.create_all(bind=engine)

configure_logging()

app = FastAPI(title="RecoveryOS")

razorpay_client = razorpay.Client(
    auth=(
        settings.razorpay_key_id,
        settings.razorpay_key_secret,
    )
)

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)

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

@app.get("/test-checkout", response_class=HTMLResponse)
def test_checkout(request: Request):

    order = razorpay_client.order.create({
        "amount": 50000,
        "currency": "INR",
        "receipt": "recoveryos_test",
    })

    return templates.TemplateResponse(
        request=request,
        name="test_checkout.html",
        context={
            "razorpay_key_id": settings.razorpay_key_id,
            "amount": order["amount"],
            "currency": order["currency"],
            "order_id": order["id"],
        },
    )