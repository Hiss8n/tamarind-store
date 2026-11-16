from fastapi import FastAPI,Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from db.routes import router as orders_router 
from fastapi.responses import JSONResponse

api = FastAPI()
api.include_router(orders_router)

""" @api.get("/")
async def read_root():
    return {"message": "Hello World"}
 """
app = CORSMiddleware(
    app=api,
    allow_origins=["http://localhost:5173", "https://tamarind-store.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@api.post("/webhook")
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






