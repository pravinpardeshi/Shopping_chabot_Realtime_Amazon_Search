"""
Product Catalog Service — agentic backend for the AI Shopping Chatbot.
Provides a structured catalog of shoes and books with vendor pricing.
"""
import random
from typing import Optional
from config import config

CATALOG = {
    # ──────────────── SHOES ────────────────
    "brooks_glycerin": {
        "id": "brooks_glycerin",
        "name": "Brooks Glycerin 21",
        "brand": "Brooks",
        "category": "shoes",
        "description": "Maximum cushioning, ultra-plush ride for long runs.",
        "available_sizes": ["7", "7.5", "8", "8.5", "9", "9.5", "10", "10.5", "11", "12"],
        "available_widths": ["B", "D", "2E", "4E"],
        "base_price": 159.95,
        "image_url": "/static/brooks_glycerin.png",
        "tags": ["running", "cushioned", "neutral"],
    },
    "brooks_ghost": {
        "id": "brooks_ghost",
        "name": "Brooks Ghost 16",
        "brand": "Brooks",
        "category": "shoes",
        "description": "Everyday trainer with smooth, balanced cushioning.",
        "available_sizes": ["7", "7.5", "8", "8.5", "9", "9.5", "10", "10.5", "11", "12"],
        "available_widths": ["B", "D", "2E"],
        "base_price": 139.95,
        "image_url": "/static/brooks_glycerin.png",
        "tags": ["running", "everyday", "neutral"],
    },
    "asics_gel_nimbus": {
        "id": "asics_gel_nimbus",
        "name": "ASICS Gel-Nimbus 26",
        "brand": "ASICS",
        "category": "shoes",
        "description": "Premium plush cushioning with GEL technology for all-day comfort.",
        "available_sizes": ["7", "7.5", "8", "8.5", "9", "9.5", "10", "10.5", "11", "12", "13"],
        "available_widths": ["D", "2E", "4E"],
        "base_price": 169.95,
        "image_url": "/static/asics_gel_nimbus.png",
        "tags": ["running", "cushioned", "neutral"],
    },
    "asics_gel_kayano": {
        "id": "asics_gel_kayano",
        "name": "ASICS Gel-Kayano 31",
        "brand": "ASICS",
        "category": "shoes",
        "description": "Stability shoe with dynamic DuoMax support system.",
        "available_sizes": ["7", "7.5", "8", "8.5", "9", "9.5", "10", "10.5", "11", "12"],
        "available_widths": ["D", "2E"],
        "base_price": 159.95,
        "image_url": "/static/asics_gel_nimbus.png",
        "tags": ["running", "stability", "support"],
    },
    "nike_air_max": {
        "id": "nike_air_max",
        "name": "Nike Air Max 270",
        "brand": "Nike",
        "category": "shoes",
        "description": "Lifestyle sneaker with full-length Air cushioning unit.",
        "available_sizes": ["7", "7.5", "8", "8.5", "9", "9.5", "10", "10.5", "11", "12", "13"],
        "available_widths": ["D"],
        "base_price": 150.00,
        "image_url": "/static/nike_air_max.png",
        "tags": ["lifestyle", "casual", "air"],
    },
    "nike_pegasus": {
        "id": "nike_pegasus",
        "name": "Nike Air Zoom Pegasus 41",
        "brand": "Nike",
        "category": "shoes",
        "description": "Versatile daily trainer with responsive Zoom Air cushioning.",
        "available_sizes": ["7", "7.5", "8", "8.5", "9", "9.5", "10", "10.5", "11", "12"],
        "available_widths": ["D", "2E"],
        "base_price": 140.00,
        "image_url": "/static/nike_air_max.png",
        "tags": ["running", "everyday", "zoom"],
    },
    "new_balance_990": {
        "id": "new_balance_990",
        "name": "New Balance 990v6",
        "brand": "New Balance",
        "category": "shoes",
        "description": "Iconic heritage runner. Made in USA. Premium ENCAP midsole.",
        "available_sizes": ["7", "7.5", "8", "8.5", "9", "9.5", "10", "10.5", "11", "12", "13"],
        "available_widths": ["D", "2E", "4E"],
        "base_price": 199.99,
        "image_url": "/static/new_balance_990.png",
        "tags": ["heritage", "lifestyle", "made in USA"],
    },
    "new_balance_fresh_foam_1080": {
        "id": "new_balance_fresh_foam_1080",
        "name": "New Balance Fresh Foam X 1080v14",
        "brand": "New Balance",
        "category": "shoes",
        "description": "Ultra-plush Fresh Foam X midsole for maximum comfort.",
        "available_sizes": ["7", "7.5", "8", "8.5", "9", "9.5", "10", "10.5", "11", "12"],
        "available_widths": ["B", "D", "2E"],
        "base_price": 164.99,
        "image_url": "/static/new_balance_990.png",
        "tags": ["running", "cushioned", "neutral"],
    },
    "hoka_bondi": {
        "id": "hoka_bondi",
        "name": "Hoka Bondi 9",
        "brand": "Hoka",
        "category": "shoes",
        "description": "Maximum underfoot cushioning. The most cushioned shoe in the Hoka lineup.",
        "available_sizes": ["7", "7.5", "8", "8.5", "9", "9.5", "10", "10.5", "11", "12", "13", "14"],
        "available_widths": ["D", "2E"],
        "base_price": 174.99,
        "image_url": "/static/hoka_bondi.png",
        "tags": ["running", "max cushion", "neutral"],
    },
    "hoka_clifton": {
        "id": "hoka_clifton",
        "name": "Hoka Clifton 9",
        "brand": "Hoka",
        "category": "shoes",
        "description": "Lightweight everyday trainer with consistent cushioning.",
        "available_sizes": ["7", "7.5", "8", "8.5", "9", "9.5", "10", "10.5", "11", "12"],
        "available_widths": ["D", "2E"],
        "base_price": 145.00,
        "image_url": "/static/hoka_bondi.png",
        "tags": ["running", "lightweight", "everyday"],
    },
    "saucony_ride": {
        "id": "saucony_ride",
        "name": "Saucony Ride 17",
        "brand": "Saucony",
        "category": "shoes",
        "description": "Smooth, cushioned ride with PWRRUN foam for everyday training.",
        "available_sizes": ["7", "7.5", "8", "8.5", "9", "9.5", "10", "10.5", "11", "12"],
        "available_widths": ["D", "2E"],
        "base_price": 139.95,
        "image_url": "/static/brooks_glycerin.png",
        "tags": ["running", "cushioned", "neutral"],
    },
    "saucony_triumph": {
        "id": "saucony_triumph",
        "name": "Saucony Triumph 22",
        "brand": "Saucony",
        "category": "shoes",
        "description": "Top-tier plush cushioning with PWRRUN+ foam.",
        "available_sizes": ["7", "7.5", "8", "8.5", "9", "9.5", "10", "10.5", "11", "12"],
        "available_widths": ["D", "2E"],
        "base_price": 159.95,
        "image_url": "/static/brooks_glycerin.png",
        "tags": ["running", "plush", "neutral"],
    },

    # ──────────────── BOOKS ────────────────
    "atomic_habits": {
        "id": "atomic_habits",
        "name": "Atomic Habits",
        "brand": "James Clear",
        "category": "books",
        "description": "A proven system for building good habits and breaking bad ones.",
        "base_price": 27.99,
        "image_url": "/static/books.png",
        "tags": ["self-help", "productivity", "habits"],
    },
    "7_habits": {
        "id": "7_habits",
        "name": "The 7 Habits of Highly Effective People",
        "brand": "Stephen R. Covey",
        "category": "books",
        "description": "A principle-centered approach for solving personal and professional problems.",
        "base_price": 22.99,
        "image_url": "/static/books.png",
        "tags": ["self-help", "leadership", "classic"],
    },
    "clean_code": {
        "id": "clean_code",
        "name": "Clean Code",
        "brand": "Robert C. Martin",
        "category": "books",
        "description": "A handbook of agile software craftsmanship.",
        "base_price": 44.99,
        "image_url": "/static/books.png",
        "tags": ["programming", "software engineering", "technical"],
    },
    "pragmatic_programmer": {
        "id": "pragmatic_programmer",
        "name": "The Pragmatic Programmer",
        "brand": "David Thomas & Andrew Hunt",
        "category": "books",
        "description": "Your journey to mastery as a software developer.",
        "base_price": 49.99,
        "image_url": "/static/books.png",
        "tags": ["programming", "software engineering", "technical"],
    },
    "ddia": {
        "id": "ddia",
        "name": "Designing Data-Intensive Applications",
        "brand": "Martin Kleppmann",
        "category": "books",
        "description": "The principles behind reliable, scalable, and maintainable systems.",
        "base_price": 59.99,
        "image_url": "/static/books.png",
        "tags": ["programming", "systems design", "backend"],
    },
    "zero_to_one": {
        "id": "zero_to_one",
        "name": "Zero to One",
        "brand": "Peter Thiel",
        "category": "books",
        "description": "Notes on startups, or how to build the future.",
        "base_price": 24.99,
        "image_url": "/static/books.png",
        "tags": ["business", "startup", "entrepreneurship"],
    },
    "sapiens": {
        "id": "sapiens",
        "name": "Sapiens: A Brief History of Humankind",
        "brand": "Yuval Noah Harari",
        "category": "books",
        "description": "A gripping best-seller exploring the history of human species.",
        "base_price": 25.99,
        "image_url": "/static/books.png",
        "tags": ["history", "science", "bestseller"],
    },
    "thinking_fast_and_slow": {
        "id": "thinking_fast_and_slow",
        "name": "Thinking, Fast and Slow",
        "brand": "Daniel Kahneman",
        "category": "books",
        "description": "Explores the dual systems that drive how we think and make choices.",
        "base_price": 23.99,
        "image_url": "/static/books.png",
        "tags": ["psychology", "science", "decision making"],
    },
    "lean_startup": {
        "id": "lean_startup",
        "name": "The Lean Startup",
        "brand": "Eric Ries",
        "category": "books",
        "description": "How continuous innovation creates successful businesses.",
        "base_price": 26.99,
        "image_url": "/static/books.png",
        "tags": ["business", "startup", "methodology"],
    },
    "deep_work": {
        "id": "deep_work",
        "name": "Deep Work",
        "brand": "Cal Newport",
        "category": "books",
        "description": "Rules for focused success in a distracted world.",
        "base_price": 25.99,
        "image_url": "/static/books.png",
        "tags": ["productivity", "focus", "self-help"],
    },
}

VENDORS = config.VENDORS


class CatalogService:
    def search(self, query: str, category: Optional[str] = None, size: Optional[str] = None, max_price: Optional[float] = None) -> list[dict]:
        """Full-text + category-aware product search with optional price filtering."""
        query_lower = query.lower()
        results = []

        for product in CATALOG.values():
            # Category filter
            if category and product["category"] != category.lower():
                continue
            
            # Price filter
            if max_price is not None:
                try:
                    m_price = float(max_price)
                    if product["base_price"] > m_price:
                        continue
                except (ValueError, TypeError):
                    pass

            # Relevance scoring
            score = 0
            searchable = (
                product["name"] + " " + product["brand"] + " " + product["category"] + " " + " ".join(product.get("tags", []))
            ).lower()

            for word in query_lower.split():
                if word in searchable:
                    score += 1

            if score == 0:
                continue

            results.append({**product, "_score": score})

        results.sort(key=lambda x: x["_score"], reverse=True)

        # Apply size filter for shoes after ranking
        filtered = []
        for r in results:
            if size and r["category"] == "shoes":
                if size not in r.get("available_sizes", []):
                    continue
            filtered.append(r)

        return filtered[:config.DEFAULT_SEARCH_RESULTS_LIMIT]  # Return configured limit

    def get_vendor_prices(self, product_id: str, width: Optional[str] = None, quantity: int = 1) -> list[dict]:
        """Get simulated prices from multiple vendors for a given product."""
        product = CATALOG.get(product_id)
        if not product:
            return []

        base = product["base_price"]
        vendor_list = VENDORS.get(product["category"], VENDORS["books"])
        offers = []

        for vendor in vendor_list:
            price = round(base + random.uniform(-base * config.PRICE_VARIATION_RANGE, base * config.PRICE_VARIATION_RANGE), 2)
            discount = 0
            if random.random() > config.DISCOUNT_PROBABILITY:
                discount = round(price * random.uniform(config.DISCOUNT_RANGE[0], config.DISCOUNT_RANGE[1]), 2)

            unit_final_price = round(price - discount, 2)
            total_price = round(unit_final_price * quantity, 2)

            offers.append({
                "vendor": vendor,
                "product_id": product_id,
                "product_name": product["name"],
                "category": product["category"],
                "size": None,  # Will be filled in by agent
                "width": width,
                "quantity": quantity,
                "unit_price": price,
                "unit_discount": discount,
                "unit_final_price": unit_final_price,
                "price": price, # Backwards compatibility for UI
                "discount": discount, # Backwards compatibility for UI
                "final_price": unit_final_price, # Backwards compatibility for unit price display
                "total_price": total_price,
                "in_stock": True,
                "image_url": product["image_url"],
            })

        return sorted(offers, key=lambda x: x["unit_final_price"])

    def get_product(self, product_id: str) -> Optional[dict]:
        return CATALOG.get(product_id)

    def get_all_categories(self) -> list[str]:
        return list(set(p["category"] for p in CATALOG.values()))


catalog_service = CatalogService()
