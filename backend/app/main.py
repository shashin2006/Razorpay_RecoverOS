from fastapi import FastAPI, Depends, Request, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

import razorpay
from pathlib import Path
import re

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
        "http://127.0.0.1:8000",
        "http://localhost:8000",
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


class TestCheckoutOrderRequest(BaseModel):
    amount: int = Field(..., ge=100, le=10_000_000)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    description: str = Field(
        default="RecoveryOS Revenue Recovery Test",
        min_length=3,
        max_length=120,
    )
    customer_name: str = Field(..., min_length=2, max_length=80)
    customer_email: str = Field(..., min_length=5, max_length=120)
    customer_contact: str = Field(..., min_length=10, max_length=15)

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: str) -> str:
        value = value.upper().strip()
        if value != "INR":
            raise ValueError("RecoveryOS Test Console currently supports INR only.")
        return value

    @field_validator("customer_email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value):
            raise ValueError("Enter a valid customer email.")
        return value

    @field_validator("customer_contact")
    @classmethod
    def validate_contact(cls, value: str) -> str:
        digits = re.sub(r"\D", "", value)
        if len(digits) != 10:
            raise ValueError("Enter a valid 10-digit Indian mobile number.")
        return digits


@app.post("/api/test-checkout/order")
def create_test_checkout_order(payload: TestCheckoutOrderRequest):
    """
    Create a real Razorpay Test Mode order from user-entered
    Test Console inputs.

    The amount is received in INR rupees from the UI and converted
    to paise before calling Razorpay.
    """
    try:
        receipt = f"recoveryos_{__import__('secrets').token_hex(6)}"

        order = razorpay_client.order.create({
            "amount": payload.amount * 100,
            "currency": payload.currency,
            "receipt": receipt,
            "notes": {
                "recoveryos_test": "true",
                "customer_name": payload.customer_name,
                "customer_email": payload.customer_email,
            },
        })

        return {
            "ok": True,
            "order_id": order["id"],
            "amount": order["amount"],
            "currency": order["currency"],
            "receipt": order.get("receipt"),
            "customer": {
                "name": payload.customer_name,
                "email": payload.customer_email,
                "contact": payload.customer_contact,
            },
            "description": payload.description,
            "environment": "Razorpay Test Mode",
        }

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Unable to create Razorpay Test Mode order: {str(exc)}",
        )


@app.get("/test-checkout", response_class=HTMLResponse)
def test_checkout(request: Request):
    """
    Render the dynamic Test Console.

    No payment order is created until the user submits
    the Test Console form.
    """
    return templates.TemplateResponse(
        request=request,
        name="test_checkout.html",
        context={
            "razorpay_key_id": settings.razorpay_key_id,
        },
    )
