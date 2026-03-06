# Configuration Management Guide

## Overview
The AI Shopping Assistant uses a centralized configuration system through `config.py` to manage all application settings, making it easy to deploy across different environments (development, testing, production).

## Configuration Files

### 1. `config.py` - Main Configuration
Contains all configuration parameters organized by category:
- Application settings (host, port, debug)
- AI/LLM configuration (Ollama settings)
- Payment gateway settings (WorldPay)
- Business logic parameters
- UI configuration
- Tool schemas
- Error messages

### 2. `.env` - Environment Variables
Runtime configuration that overrides defaults:
```bash
# Copy the example file
cp .env.example .env
# Edit with your actual values
```

## Configuration Categories

### 🖥️ Application Settings
```python
APP_NAME = "AI Shopping Agent"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8001"))
```

### 🤖 AI/LLM Configuration
```python
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")
MAX_AGENT_ITERATIONS = int(os.getenv("MAX_AGENT_ITERATIONS", "10"))
```

### 💳 Payment Configuration
```python
WORLDPAY_BASE_URL = os.getenv("WORLDPAY_BASE_URL", "https://try.access.worldpay.com")
WORLDPAY_USERNAME = os.getenv("WORLDPAY_USERNAME", "")
WORLDPAY_PASSWORD = os.getenv("WORLDPAY_PASSWORD", "")
WORLDPAY_MERCHANT_ENTITY = os.getenv("WORLDPAY_MERCHANT_ENTITY", "")
```

### 📦 Business Logic
```python
DEFAULT_SEARCH_RESULTS_LIMIT = int(os.getenv("DEFAULT_SEARCH_RESULTS_LIMIT", "6"))
PRICE_VARIATION_RANGE = float(os.getenv("PRICE_VARIATION_RANGE", "0.12"))
DISCOUNT_PROBABILITY = float(os.getenv("DISCOUNT_PROBABILITY", "0.6"))
```

## Environment-Specific Configurations

### Development (Default)
```python
class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = "DEBUG"
```

### Production
```python
class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = "WARNING"
    # Requires WorldPay credentials
```

### Testing
```python
class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    WORLDPAY_BASE_URL = "https://api.test.worldpay.com"
```

## Usage Examples

### Setting Environment
```bash
# Development (default)
export ENVIRONMENT=development

# Production
export ENVIRONMENT=production

# Testing
export ENVIRONMENT=testing
```

### Custom Configuration
```python
from config import config

# Access any configuration parameter
model = config.OLLAMA_MODEL
port = config.PORT
timeout = config.WORLDPAY_TIMEOUT

# Access nested configurations
ui_config = config.UI_CONFIG
tool_schemas = config.TOOL_SCHEMAS
```

## Configuration Validation

The system automatically validates configuration on startup:

```python
# Validates required production settings
if isinstance(config, ProductionConfig):
    if not config.WORLDPAY_USERNAME:
        raise ValueError("WORLDPAY_USERNAME is required in production")
```

## Key Benefits

1. **Centralized Management**: All settings in one place
2. **Environment-Specific**: Easy deployment across environments
3. **Type Safety**: Proper type conversion and validation
4. **Documentation**: Self-documenting configuration structure
5. **Flexibility**: Easy to add new parameters
6. **Security**: Sensitive data in environment variables

## Common Configuration Tasks

### Changing the AI Model
```bash
# In .env
OLLAMA_MODEL=llama3.2
OLLAMA_BASE_URL=http://your-ollama-server:11434
```

### Updating Business Logic
```python
# In config.py
DEFAULT_SEARCH_RESULTS_LIMIT = 10
PRICE_VARIATION_RANGE = 0.15  # 15% price variation
```

### Adding New Vendors
```python
VENDORS = {
    "shoes": ["Amazon", "Zappos", "New Vendor"],
    "books": ["Amazon", "Barnes & Noble", "New Book Vendor"]
}
```

## Migration Notes

All hardcoded values have been moved to `config.py`:
- Tool schemas → `config.TOOL_SCHEMAS`
- System prompts → `config.AGENT_SYSTEM_PROMPT`
- UI text → `config.UI_CONFIG`
- Error messages → `config.ERROR_MESSAGES`
- Business parameters → Various config attributes

This makes the application more maintainable and easier to configure for different deployment scenarios.
