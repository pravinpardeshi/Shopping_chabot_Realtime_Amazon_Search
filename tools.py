"""
Consolidated Tool Registry — defines both schemas and implementations for the Shopping Agent.
"""
import json
import logging
from catalog_service import catalog_service
from shopping_service import shopping_service
from payment_service import payment_service
from config import config

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# TOOLS SCHEMA
# ──────────────────────────────────────────────────────────────────────────────

TOOL_SCHEMAS = config.TOOL_SCHEMAS

# ──────────────────────────────────────────────────────────────────────────────
# TOOLS IMPLEMENTATION
# ──────────────────────────────────────────────────────────────────────────────

def search_products(query: str, category: str = None, size: str = None, max_price: float = None, **kwargs) -> dict:
    """
    Search for products using real-time Amazon data + catalog service.
    """
    if max_price is not None:
        try:
            max_price = float(max_price)
        except (ValueError, TypeError):
            max_price = None
    
    # Try to extract product details from query for better Amazon search
    product_details = {
        "product_name": query,
        "size": size,
        "category": category
    }
    
    # Get real-time results from shopping service (includes Amazon)
    amazon_results = shopping_service.search_product(product_details)
    
    # Also get catalog results as fallback
    catalog_results = catalog_service.search(query, category=category, size=size, max_price=max_price)
    
    # Combine results, prioritizing Amazon data
    all_results = []
    
    # Add Amazon results first
    for result in amazon_results:
        all_results.append({
            "id": result.get("asin", f"amazon_{len(all_results)}"),
            "name": result.get("product_name", "Unknown Product"),
            "brand": "Amazon",
            "category": category or "General",
            "description": f"Real-time Amazon result - {result.get('vendor', 'Amazon')}",
            "base_price": result.get("price", 0.0),
            "final_price": result.get("final_price", 0.0),
            "image_url": result.get("image_url"),
            "vendor": result.get("vendor", "Amazon"),
            "rating": result.get("rating"),
            "reviews": result.get("reviews"),
            "is_prime": result.get("is_prime"),
            "product_url": result.get("product_url"),
            "is_real_amazon": True
        })
    
    # Add catalog results as fallback
    for result in catalog_results:
        # Avoid duplicates by checking if we already have this product
        if not any(r["name"] == result["name"] for r in all_results):
            all_results.append({
                "id": result["id"],
                "name": result["name"],
                "brand": result["brand"],
                "category": result["category"],
                "description": result["description"],
                "base_price": result["base_price"],
                "image_url": result.get("image_url"),
                "vendor": "Catalog",
                "is_real_amazon": False
            })
    
    if not all_results:
        return {"found": False, "message": f"No products found matching '{query}'."}

    return {
        "found": True,
        "count": len(all_results),
        "products": all_results
    }

def get_best_offer(product_id: str, quantity: int = None, **kwargs) -> dict:
    # Ensure quantity is an integer
    if quantity is None:
        quantity = config.DEFAULT_QUANTITY
    try:
        quantity = int(quantity)
    except (ValueError, TypeError):
        quantity = config.DEFAULT_QUANTITY
    
    # For Amazon products, we need to handle differently
    if product_id.startswith("amazon_") or kwargs.get("is_real_amazon"):
        # Create a mock offer for Amazon products
        return {
            "found": True, 
            "best_offer": {
                "product_id": product_id,
                "product_name": kwargs.get("product_name", "Amazon Product"),
                "vendor": "Amazon",
                "unit_base_price": kwargs.get("price", 0.0),
                "unit_final_price": kwargs.get("final_price", 0.0),
                "total_price": kwargs.get("final_price", 0.0) * quantity,
                "quantity": quantity,
                "image_url": kwargs.get("image_url"),
                "product_url": kwargs.get("product_url"),
                "is_prime": kwargs.get("is_prime", False)
            }
        }
    
    # Use catalog service for non-Amazon products
    offers = catalog_service.get_vendor_prices(product_id, quantity=quantity)
    if not offers:
        return {"found": False, "message": "No offers available."}

    best = min(offers, key=lambda x: x["unit_final_price"])
    return {"found": True, "best_offer": best}

def initiate_checkout(product_id: str, quantity: int = None, **kwargs) -> dict:
    # Ensure quantity is an integer
    if quantity is None:
        quantity = config.DEFAULT_QUANTITY
    try:
        quantity = int(quantity)
    except (ValueError, TypeError):
        quantity = config.DEFAULT_QUANTITY
    
    # For Amazon products
    if product_id.startswith("amazon_") or kwargs.get("is_real_amazon"):
        price = kwargs.get("final_price", 0.0)
        return {
            "success": True, 
            "message": f"✅ Checkout UI triggered for {quantity} unit(s) of Amazon product.",
            "checkout_details": {"product_id": product_id, "quantity": quantity},
            "offer_details": {
                "product_id": product_id,
                "product_name": kwargs.get("product_name", "Amazon Product"),
                "vendor": "Amazon",
                "unit_base_price": price,
                "unit_final_price": price,
                "total_price": price * quantity,
                "quantity": quantity,
                "image_url": kwargs.get("image_url"),
                "product_url": kwargs.get("product_url"),
                "is_prime": kwargs.get("is_prime", False)
            }
        }
    
    # Get the best offer for catalog products
    offers = catalog_service.get_vendor_prices(product_id, quantity=quantity)
    if not offers:
        return {"success": False, "message": "No offers available for checkout."}
    
    # Find the best offer by unit_final_price
    best = min(offers, key=lambda x: x["unit_final_price"])
    return {
        "success": True, 
        "message": f"✅ Checkout UI triggered for {quantity} unit(s) of '{product_id}'.",
        "checkout_details": {"product_id": product_id, "quantity": quantity},
        "offer_details": best  # Include offer details for frontend
    }

def process_payment(**kwargs) -> dict:
    return payment_service.process_payment(**kwargs)

# ──────────────────────────────────────────────────────────────────────────────
# EXECUTION ENGINE
# ──────────────────────────────────────────────────────────────────────────────

TOOL_MAP = {
    "search_products": search_products,
    "get_best_offer": get_best_offer,
    "initiate_checkout": initiate_checkout,
    "process_payment": process_payment,
}

def execute_tool(name: str, arguments: dict) -> dict:
    func = TOOL_MAP.get(name)
    if not func:
        return {"error": f"Tool '{name}' not found."}
    try:
        if isinstance(arguments, str):
            arguments = json.loads(arguments)
        return func(**arguments)
    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        return {"error": str(e)}
