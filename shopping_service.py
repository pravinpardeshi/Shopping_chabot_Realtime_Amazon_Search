import random
import logging
from amazon_product_search3 import query_amazon_direct

logger = logging.getLogger(__name__)

class ShoppingService:
    def __init__(self):
        self.vendors = ["Amazon", "Zappos", "Road Runner Sports", "Dick's Sporting Goods"]

    def search_product(self, product_details: dict):
        """
        Searches for products across different vendors, including real-time Amazon data.
        """
        if not product_details:
            return []

        results = []
        
        # Build search query for Amazon
        search_query = self._build_search_query(product_details)
        
        # Get real-time Amazon results
        amazon_results = self._search_amazon(search_query)
        
        # Add Amazon results to our results
        for amazon_product in amazon_results[:5]:  # Limit to top 5 Amazon results
            results.append({
                "vendor": "Amazon",
                "product_name": amazon_product["title"],
                "size": product_details.get("size"),
                "width": product_details.get("width"),
                "price": self._parse_price(amazon_product["price"]),
                "discount": 0,
                "final_price": self._parse_price(amazon_product["price"]),
                "in_stock": True,
                "image_url": amazon_product["image"],
                "rating": amazon_product["rating"],
                "reviews": amazon_product["reviews"],
                "is_prime": amazon_product["is_prime"],
                "product_url": amazon_product["url"],
                "asin": amazon_product["asin"]
            })
        
        # Add simulated results from other vendors
        base_price = random.uniform(120, 160)
        for vendor in self.vendors[1:]:  # Skip Amazon as we already have real data
            price = round(base_price + random.uniform(-10, 10), 2)
            discount = 0
            if random.random() > 0.7:
                discount = round(price * random.uniform(0.05, 0.15), 2)
            
            results.append({
                "vendor": vendor,
                "product_name": product_details.get("product_name"),
                "size": product_details.get("size"),
                "width": product_details.get("width"),
                "price": price,
                "discount": discount,
                "final_price": round(price - discount, 2),
                "in_stock": True,
                "image_url": "/static/brooks_glycerin.png" if product_details.get("product_name") and ("glycerin" in product_details.get("product_name").lower() or "brooks" in product_details.get("product_name").lower()) else None
            })
        
        return results

    def _build_search_query(self, product_details: dict):
        """Build a search query from product details."""
        query_parts = []
        
        if product_details.get("product_name"):
            query_parts.append(product_details["product_name"])
        
        if product_details.get("size"):
            query_parts.append(f"size {product_details['size']}")
        
        if product_details.get("width"):
            query_parts.append(product_details["width"])
        
        return " ".join(query_parts)

    def _search_amazon(self, search_query):
        """Search Amazon for products using the real-time API."""
        try:
            logger.info(f"Searching Amazon for: {search_query}")
            amazon_results = query_amazon_direct(search_query)
            logger.info(f"Found {len(amazon_results)} Amazon products")
            return amazon_results
        except Exception as e:
            logger.error(f"Error searching Amazon: {e}")
            return []

    def _parse_price(self, price_str):
        """Parse price string to float."""
        if not price_str or price_str == "N/A":
            return 0.0
        
        try:
            # Remove currency symbols and convert to float
            import re
            price_clean = re.sub(r'[^\d.]', '', price_str)
            return float(price_clean) if price_clean else 0.0
        except (ValueError, AttributeError):
            return 0.0

    def get_best_offer(self, results: list):
        if not results:
            return None
        return min(results, key=lambda x: x["final_price"])

shopping_service = ShoppingService()
