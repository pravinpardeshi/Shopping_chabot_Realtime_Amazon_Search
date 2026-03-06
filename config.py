"""
Configuration Management for AI Shopping Assistant

Centralizes all configuration parameters including:
- Model settings
- API endpoints  
- Database connections
- UI settings
- Business logic parameters
"""

import os
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class"""
    
    # ── Application Settings ──────────────────────────────────────────────
    APP_NAME = "AI Shopping Agent"
    APP_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8001"))
    
    # ── AI/LLM Configuration ─────────────────────────────────────────────
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")
    OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "30"))
    MAX_AGENT_ITERATIONS = int(os.getenv("MAX_AGENT_ITERATIONS", "10"))
    
    # ── WorldPay Payment Configuration ───────────────────────────────────
    WORLDPAY_BASE_URL = os.getenv("WORLDPAY_BASE_URL", "https://try.access.worldpay.com")
    WORLDPAY_USERNAME = os.getenv("WORLDPAY_USERNAME", "")
    WORLDPAY_PASSWORD = os.getenv("WORLDPAY_PASSWORD", "")
    WORLDPAY_MERCHANT_ENTITY = os.getenv("WORLDPAY_MERCHANT_ENTITY", "")
    WORLDPAY_API_VERSION = "application/vnd.worldpay.payments-v7+json"
    WORLDPAY_TIMEOUT = int(os.getenv("WORLDPAY_TIMEOUT", "30"))
    
    # ── Catalog & Business Logic ─────────────────────────────────────────
    DEFAULT_SEARCH_RESULTS_LIMIT = int(os.getenv("DEFAULT_SEARCH_RESULTS_LIMIT", "6"))
    MAX_SEARCH_RESULTS_LIMIT = int(os.getenv("MAX_SEARCH_RESULTS_LIMIT", "20"))
    DEFAULT_QUANTITY = int(os.getenv("DEFAULT_QUANTITY", "1"))
    MAX_QUANTITY = int(os.getenv("MAX_QUANTITY", "10"))
    
    # Pricing configuration
    PRICE_VARIATION_RANGE = float(os.getenv("PRICE_VARIATION_RANGE", "0.12"))  # ±12%
    DISCOUNT_PROBABILITY = float(os.getenv("DISCOUNT_PROBABILITY", "0.6"))  # 60% chance
    DISCOUNT_RANGE = (0.05, 0.18)  # 5% to 18% discount range
    
    # ── UI Configuration ───────────────────────────────────────────────────
    UI_CONFIG = {
        "app_name": "ShopAgent",
        "logo_icon": "🛍️",
        "welcome_message": "Hi! I'm your AI Shopping Agent powered by Llama 3.1.",
        "capabilities_message": "I can autonomously search our catalog of shoes and books, compare prices across vendors, and find you the best deal.",
        "examples": [
            "Show me Brooks Glycerin size 9.5 2E",
            "Best running shoes under $150", 
            "Find Atomic Habits book",
            "Show me Hoka running shoes"
        ]
    }
    
    # ── Agent System Prompt Configuration ───────────────────────────────────
    AGENT_SYSTEM_PROMPT = """
You are an AI-powered shopping assistant for an e-commerce platform.
Your role is to:

Show available products clearly when the user enters the store. use 'search_products' for showing & searching products. Show offers when available using 'get_best_offer' 

Help the user explore products (search, filter, categories).

Confirm product selection before purchase.

Ask for confirmation on the order before proceeding with the checkout. 

When user says "checkout", "payment", "buy", "purchase", "pay", or similar terms, and you have a confirmed product/offer, only then use 'initiate_checkout' to show the popup for user to enter the Credit Card details. 

You must follow a structured conversational flow.
"""
    
    # ── Tool Configuration ─────────────────────────────────────────────────
    TOOL_SCHEMAS = [
        {
            "type": "function",
            "function": {
                "name": "search_products",
                "description": "Search for products (shoes, books, etc.) in the catalog. Prerequisite for buying.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search term, e.g. 'Brooks shoe'"},
                        "category": {"type": "string", "enum": ["shoes", "books"], "description": "Optional category filter"},
                        "size": {"type": "string", "description": "Shoe size (optional)"},
                        "max_price": {"type": "number", "description": "Maximum price limit (optional)"}
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_best_offer",
                "description": "Get the best price for a specific product. Prerequisite for checkout.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_id": {"type": "string", "description": "The product ID, e.g. 'brooks_ghost'"},
                        "quantity": {"type": "integer", "description": "Units to purchase (default 1)", "minimum": 1}
                    },
                    "required": ["product_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "initiate_checkout",
                "description": "Triggers the secure payment UI. Call this IMMEDIATELY when the user confirms they want to buy.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_id": {"type": "string", "description": "The product ID to purchase"},
                        "quantity": {"type": "integer", "description": "Units to purchase", "minimum": 1}
                    },
                    "required": ["product_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "process_payment",
                "description": "Process payment if user provides card details in chat.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "amount": {"type": "number"},
                        "card_type": {"type": "string", "enum": ["Visa", "Mastercard"]},
                        "card_number": {"type": "string"},
                        "card_expiry": {"type": "string"},
                        "card_cvc": {"type": "string"}
                    },
                    "required": ["amount", "card_type", "card_number", "card_expiry", "card_cvc"]
                }
            }
        }
    ]
    
    # ── Product Catalog Configuration ───────────────────────────────────────
    PRODUCT_CATEGORIES = ["shoes", "books"]
    
    VENDORS = {
        "shoes": ["Amazon", "Zappos", "Road Runner Sports", "Dick's Sporting Goods", "Running Warehouse"],
        "books": ["Amazon", "Barnes & Noble", "ThriftBooks", "Book Depository", "eBay Books"],
    }
    
    # ── Session Management ───────────────────────────────────────────────────
    SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", "60"))
    MAX_SESSIONS = int(os.getenv("MAX_SESSIONS", "1000"))
    
    # ── Logging Configuration ─────────────────────────────────────────────────
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # ── Security Configuration ───────────────────────────────────────────────
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour
    
    # ── Static File Configuration ─────────────────────────────────────────────
    STATIC_DIR = "./static"
    TEMPLATES_DIR = "./templates"
    
    # ── Validation Rules ─────────────────────────────────────────────────────
    VALIDATION_RULES = {
        "card_number": {"length": 16, "pattern": r"^\d{16}$"},
        "card_expiry": {"pattern": r"^\d{2}/\d{2}$"},
        "card_cvc": {"length": [3, 4], "pattern": r"^\d{3,4}$"},
        "zip_code": {"max_length": 10},
        "state": {"max_length": 2}
    }
    
    # ── Error Messages ───────────────────────────────────────────────────────
    ERROR_MESSAGES = {
        "no_products_found": "No products found matching your search.",
        "no_offers_available": "No offers available for this product.",
        "invalid_card_details": "Invalid card details provided.",
        "payment_failed": "Payment processing failed. Please try again.",
        "session_expired": "Your session has expired. Please start over.",
        "server_error": "An unexpected error occurred. Please try again."
    }
    
    # ── Success Messages ─────────────────────────────────────────────────────
    SUCCESS_MESSAGES = {
        "order_confirmed": "🎉 Order confirmed! Your purchase has been successfully processed.",
        "payment_processed": "Payment processed successfully.",
        "product_found": "Found matching products for your search."
    }


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = "WARNING"
    # Override production-specific settings here


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    # Use test database/endpoints
    WORLDPAY_BASE_URL = "https://api.test.worldpay.com"


# ── Configuration Factory ───────────────────────────────────────────────────

def get_config() -> Config:
    """Return appropriate configuration based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionConfig()
    elif env == "testing":
        return TestingConfig()
    else:
        return DevelopmentConfig()


# ── Configuration Validation ─────────────────────────────────────────────────

def validate_config(config: Config) -> List[str]:
    """Validate configuration and return list of errors"""
    errors = []
    
    # Validate required WorldPay credentials in production
    if isinstance(config, ProductionConfig):
        if not config.WORLDPAY_USERNAME:
            errors.append("WORLDPAY_USERNAME is required in production")
        if not config.WORLDPAY_PASSWORD:
            errors.append("WORLDPAY_PASSWORD is required in production")
        if not config.WORLDPAY_MERCHANT_ENTITY:
            errors.append("WORLDPAY_MERCHANT_ENTITY is required in production")
    
    # Validate port range
    if not (1 <= config.PORT <= 65535):
        errors.append("PORT must be between 1 and 65535")
    
    # Validate timeouts
    if config.OLLAMA_TIMEOUT <= 0:
        errors.append("OLLAMA_TIMEOUT must be positive")
    if config.WORLDPAY_TIMEOUT <= 0:
        errors.append("WORLDPAY_TIMEOUT must be positive")
    
    return errors


# ── Global Configuration Instance ───────────────────────────────────────────

# Initialize configuration
config = get_config()

# Validate configuration on startup
validation_errors = validate_config(config)
if validation_errors:
    raise ValueError(f"Configuration validation failed: {validation_errors}")

# Export commonly used configuration
__all__ = [
    'config',
    'Config', 
    'DevelopmentConfig',
    'ProductionConfig',
    'TestingConfig',
    'get_config',
    'validate_config'
]
