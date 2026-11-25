"""
Daraja STK Push (M-Pesa Express) with FastAPI

Install:  pip install fastapi uvicorn httpx python-dotenv
Run:      uvicorn main:app --reload --port 8000
"""

import base64
import os
from datetime import datetime
from zoneinfo import ZoneInfo

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

load_dotenv()

CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
SHORTCODE = os.getenv("SHORTCODE")          # Paybill or Till number
PASSKEY = os.getenv("PASSKEY")              # Lipa Na M-Pesa Online passkey
CALLBACK_URL = os.getenv("CALLBACK_URL")    # public HTTPS URL ending in /mpesa/callback
MPESA_ENV = os.getenv("MPESA_ENV", "sandbox")
# "CustomerPayBillOnline" for Paybill, "CustomerBuyGoodsOnline" for Till
TRANSACTION_TYPE = os.getenv("TRANSACTION_TYPE", "CustomerPayBillOnline")

BASE_URL = (
    "https://api.safaricom.co.ke"
    if MPESA_ENV == "production"
    else "https://sandbox.safaricom.co.ke"
)



# ---------- Schemas ----------

class STKPushRequest(BaseModel):
    phone: str = Field(..., examples=["0712345678"])
    amount: int = Field(..., gt=0, examples=[1])
    account_reference: str = Field("Order123", max_length=12)
    description: str = Field("Payment", max_length=13)
    order_ids: list[int] = Field(default_factory=list)


class STKQueryRequest(BaseModel):
    checkout_request_id: str = Field(..., min_length=1)


# ---------- Helpers ----------

def get_timestamp() -> str:
    return datetime.now(ZoneInfo("Africa/Nairobi")).strftime("%Y%m%d%H%M%S")


def get_password(timestamp: str) -> str:
    raw = f"{SHORTCODE}{PASSKEY}{timestamp}"
    return base64.b64encode(raw.encode()).decode()


def format_phone(phone: str) -> str:
    """Validate 07XXXXXXXX and return the M-Pesa 254XXXXXXXXX format."""
    if len(phone) != 10 or not phone.startswith("07") or not phone.isdigit():
        raise HTTPException(
            status_code=422,
            detail="Phone number must be in the format 07XXXXXXXX",
        )
    return "254" + phone[1:]


async def get_access_token(client: httpx.AsyncClient) -> str:
    resp = await client.get(
        f"{BASE_URL}/oauth/v1/generate",
        params={"grant_type": "client_credentials"},
        auth=(CONSUMER_KEY, CONSUMER_SECRET),
    )
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Token error: {resp.text}")
    return resp.json()["access_token"]


# ---------- Routes ----------




