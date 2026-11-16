from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.routes import cart_router, router as orders_router

api = FastAPI()
api.include_router(orders_router)
api.include_router(cart_router)

@api.get("/")
async def read_root():
    return {"message": "Hello World"}

app = CORSMiddleware(
    app=api,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)






def add_order(items:dict)->dict:

    order_items={
        "session_id":{"name:" ,"samosa","qty:",2}
    }


    return order_items["session_id"]


myorder=add_order({"name:","samosa","qty:",3})

print(myorder)






