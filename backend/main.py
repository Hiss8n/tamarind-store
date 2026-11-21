import os
from fastapi import FastAPI,Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from db.routes import router as orders_router 
from fastapi.responses import JSONResponse
from payment.mpesa import get_timestamp
from payment.mpesa import get_access_token
from payment.mpesa import get_password
from payment.mpesa import format_phone
from payment.mpesa import STKPushRequest
from payment.mpesa import STKQueryRequest
from payment.mpesa import BASE_URL
from db.services import update_order_status
import httpx


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


app = FastAPI()
app.include_router(orders_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://tamarind-store.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return {"message": "Hello World"}


@app.post("/webhook")
async def web_hook(req:Request):
    payload= await req.json()

    intent=payload["queryResult"]["intent"]["displayName"]
    parameters=payload["queryResult"]["parameters"]
    context_output=payload["queryResult"]["outputContexts"]

    if intent=="track.order-Context:response":
        return JSONResponse(content= {
                    "fulfillmentText": f"received {intent} from the backend code api"
                }
        )



# 1. Handle adding an order
async def add_order(params: dict, session_id: str):
    print("Adding order...")
    print("Parameters:", params)
    print("Session ID:", session_id)

    # Extract your parameters
    product = params.get("product")
    quantity = params.get("quantity")

    # TODO: Add your order processing/database logic here

    return {
        "fulfillmentText": (
            f"Your order for {quantity} {product} "
            "has been received. Would you like anything else?"
        )
    }


# 2. Handle removing an order
async def remove_order(params: dict, session_id: str):
    print("Removing order...")
    print("Parameters:", params)
    print("Session ID:", session_id)

    # Extract your parameters
    product = params.get("product")
    quantity = params.get("quantity")

    # TODO: Add your order removal/database logic here

    return {
        "fulfillmentText": (
            f"I have received your request to remove "
            f"{quantity} {product} from your order."
        )
    }


# 3. Extract parameters from Dialogflow outputContexts
def extract_context_data(query_result: dict):

    output_contexts = query_result.get("outputContexts", [])

    for context in output_contexts:

        params = context.get("parameters", {})

        if params:
            return params

    return {}


# 4. Main Dialogflow webhook endpoint
""" @api.post("/webhook")
async def dialogflow_webhook(request: Request):

    body = await request.json()

    query_result = body.get("queryResult", {})

    # Get intent name
    intent_name = (
        query_result.get("intent", {}).get("displayName", "")
    )

    # Get parameters from outputContexts
    params = extract_context_data(query_result)

    # Get session ID from the webhook request
    session = body.get("session", "")
    session_id = session.split("/")[-1] if session else ""

    # Fallback: extract session ID from outputContext name
    if not session_id:
        contexts = query_result.get("outputContexts", [])

        if contexts:
            context_name = contexts[0].get("name", "")
            parts = context_name.split("/sessions/")

            if len(parts) > 1:
                session_id = parts[1].split("/")[0]

    # Route to the correct intent handler
    if intent_name == "add.order":
        result = await add_order(params, session_id)

    elif intent_name == "remove.order":
        result = await remove_order(params, session_id)

    else:
        result = {
            "fulfillmentText": "Sorry, I don't understand that request."
        }

    return JSONResponse(content=result)
 """


""" 
get_shortcode() """

#Mpesa api routes


@app.post("/stkpush")
async def stk_push(req: STKPushRequest):
    if not all([CONSUMER_KEY, CONSUMER_SECRET, SHORTCODE, PASSKEY, CALLBACK_URL]):
        raise HTTPException(status_code=503, detail="M-Pesa configuration is incomplete")

    phone = format_phone(req.phone)
    timestamp = get_timestamp()

    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": get_password(timestamp),
        "Timestamp": timestamp,
        "TransactionType": TRANSACTION_TYPE,
        "Amount": req.amount,
        "PartyA": phone,
        "PartyB": SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": CALLBACK_URL,
        "AccountReference": req.account_reference,
        "TransactionDesc": req.description,
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            token = await get_access_token(client)
            resp = await client.post(
                f"{BASE_URL}/mpesa/stkpush/v1/processrequest",
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
            )
            data = resp.json()
    except httpx.RequestError as error:
        raise HTTPException(status_code=502, detail=f"Could not reach M-Pesa: {error}") from error

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=data)

    checkout_request_id = data.get("CheckoutRequestID")
    if checkout_request_id:
        payment_transactions[checkout_request_id] = {
            "order_ids": req.order_ids,
            "phone": phone,
            "amount": req.amount,
            "status": "processing",
        }

    return {
        "MerchantRequestID": data.get("MerchantRequestID"),
        "CheckoutRequestID": checkout_request_id,
        "ResponseCode": data.get("ResponseCode"),
        "ResponseDescription": data.get("ResponseDescription"),
        "CustomerMessage": data.get("CustomerMessage"),
    }


@app.post("/mpesa/callback")
async def mpesa_callback(request: Request):
    body = await request.json()
    print("Callback received:", body)

    cb = body.get("Body", {}).get("stkCallback", {})
    checkout_request_id = cb.get("CheckoutRequestID")
    result_code = cb.get("ResultCode")
    transaction = payment_transactions.get(checkout_request_id, {})
    order_ids = transaction.get("order_ids", [])

    if result_code == 0:
        items = cb.get("CallbackMetadata", {}).get("Item", [])
        meta = {item["Name"]: item.get("Value") for item in items}
        payment_transactions[checkout_request_id] = {
            **transaction,
            "status": "paid",
            "receipt": meta.get("MpesaReceiptNumber"),
            "amount": meta.get("Amount"),
        }
        update_order_status(order_ids, "paid")
        print("PAYMENT SUCCESS:", {
            "checkout_request_id": checkout_request_id,
            "order_ids": order_ids,
            "amount": meta.get("Amount"),
            "receipt": meta.get("MpesaReceiptNumber"),
            "phone": meta.get("PhoneNumber"),
            "date": meta.get("TransactionDate"),
        })
    else:
        payment_transactions[checkout_request_id] = {
            **transaction,
            "status": "failed",
            "result_code": result_code,
            "result_desc": cb.get("ResultDesc"),
        }
        update_order_status(order_ids, "failed")
        print(f"PAYMENT FAILED [{result_code}]: {cb.get('ResultDesc')}")

    return {"ResultCode": 0, "ResultDesc": "Accepted"}


@app.post("/stkquery")
async def stk_query(req: STKQueryRequest):
    timestamp = get_timestamp()
    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": get_password(timestamp),
        "Timestamp": timestamp,
        "CheckoutRequestID": req.checkout_request_id,
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            token = await get_access_token(client)
            resp = await client.post(
                f"{BASE_URL}/mpesa/stkpushquery/v1/query",
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
            )
            data = resp.json()
    except httpx.RequestError as error:
        raise HTTPException(status_code=502, detail=f"Could not reach M-Pesa: {error}") from error

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=data)

    local = payment_transactions.get(req.checkout_request_id)
    return {**data, "local_status": local["status"] if local else None}


# In-memory mapping used until callback processing is backed by a database table.
payment_transactions: dict[str, dict] = {}


