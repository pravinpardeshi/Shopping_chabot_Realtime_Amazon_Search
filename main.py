from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import logging
import json
from config import config

from agent import agent
from payment_service import payment_service

logging.basicConfig(level=getattr(logging, config.LOG_LEVEL), format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

app = FastAPI(title=config.APP_NAME)

app.mount("/static", StaticFiles(directory=config.STATIC_DIR), name="static")
templates = Jinja2Templates(directory=config.TEMPLATES_DIR)

# In-memory session state
sessions: dict = {}


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data.get("message", "").strip()
    session_id = data.get("session_id", "default")

    if not user_message:
        return JSONResponse({"reply": "Please type a message."})

    # Initialize session
    if session_id not in sessions:
        sessions[session_id] = {"history": [], "best_offer": None}

    session = sessions[session_id]

    # Run the agentic loop
    result = agent.chat(user_message, session["history"])

    # Update session history and context
    session["history"].extend(result["new_messages"])
    if result.get("offer_details"):
        session["best_offer"] = result["offer_details"]

    return JSONResponse({
        "reply": result["reply"],
        "offer_details": result.get("offer_details"),
        "current_context_offer": session.get("best_offer"),
        "thinking_steps": result.get("thinking_steps", []),
        "search_results": result.get("search_results", []),
        "trigger_checkout": result.get("trigger_checkout", False),
    })


@app.post("/checkout")
async def checkout(request: Request):
    data = await request.json()
    session_id = data.get("session_id", "default")
    card_type = data.get("card_type")
    card_number = data.get("card_number")
    card_expiry = data.get("card_expiry", "")
    card_cvc = data.get("card_cvc", "")
    shipping_address = data.get("shipping_address", {})

    session = sessions.get(session_id)
    if not session or not session.get("best_offer"):
        return JSONResponse({"success": False, "message": "No active purchase found. Please start a new search."})

    offer = session["best_offer"]
    product_name = offer.get("product_name", "Shopping purchase")

    if shipping_address:
        logger.info(
            f"Shipping to: {shipping_address.get('name')}, "
            f"{shipping_address.get('street')}, {shipping_address.get('city')}, "
            f"{shipping_address.get('state')} {shipping_address.get('zip')}, "
            f"{shipping_address.get('country')}"
        )
    result = payment_service.process_payment(
        amount=offer.get("total_price", offer["final_price"]),
        card_type=card_type,
        card_number=card_number,
        card_expiry=card_expiry,
        card_cvc=card_cvc,
        description=product_name[:24],
    )

    if result["success"]:
        session["best_offer"] = None
        return JSONResponse({
            "success": True,
            "message": f"🎉 Order confirmed for **{product_name}**! {result['message']}",
            "transaction_id": result["transaction_id"],
            "worldpay_outcome": result.get("worldpay_outcome"),
        })

    return JSONResponse({
        "success": False,
        "message": result["message"],
        "worldpay_outcome": result.get("worldpay_outcome"),
    })


@app.get("/catalog")
async def get_catalog():
    """Debug endpoint to view the full product catalog."""
    from .catalog_service import CATALOG
    return JSONResponse({"products": list(CATALOG.values()), "total": len(CATALOG)})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.HOST, port=config.PORT)
