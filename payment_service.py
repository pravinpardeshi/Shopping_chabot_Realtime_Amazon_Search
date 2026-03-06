"""
Payment Service — integrates with the real WorldPay Access Card Payments API.

Uses the WorldPay Access API (v7) to authorize card payments with auto-settlement.
Sandbox: https://try.access.worldpay.com
Production: https://access.worldpay.com

Credentials are loaded from environment variables (see .env).
"""
import os
import uuid
import logging
import requests
from base64 import b64encode
from config import config

logger = logging.getLogger(__name__)

# ── WorldPay configuration ──────────────────────────────────────────────────
WORLDPAY_BASE_URL = config.WORLDPAY_BASE_URL
WORLDPAY_USERNAME = config.WORLDPAY_USERNAME
WORLDPAY_PASSWORD = config.WORLDPAY_PASSWORD
WORLDPAY_MERCHANT_ENTITY = config.WORLDPAY_MERCHANT_ENTITY

API_VERSION = config.WORLDPAY_API_VERSION


def _basic_auth_header() -> str:
    """Build the Base64-encoded Basic Auth header value."""
    token = b64encode(f"{WORLDPAY_USERNAME}:{WORLDPAY_PASSWORD}".encode()).decode()
    return f"Basic {token}"


class PaymentService:
    """Processes card payments through the WorldPay Access API."""

    def process_payment(
        self,
        amount: float,
        card_type: str,
        card_number: str,
        card_expiry: str = "",
        card_cvc: str = "",
        description: str = "AI Shopping Agent purchase",
    ) -> dict:
        """
        Authorize (and auto-settle) a card payment via WorldPay.

        Args:
            amount:       Total in USD (e.g. 149.99).
            card_type:    "Visa" or "Mastercard".
            card_number:  16-digit card number (spaces/dashes accepted).
            card_expiry:  Expiry in MM/YY or MM / YY format.
            card_cvc:     3-digit CVC code.
            description:  Narrative shown on the cardholder statement.

        Returns:
            dict with 'success', 'transaction_id', 'message', and optionally
            'worldpay_outcome' and 'risk_factors'.
        """
        # ── Input validation ────────────────────────────────────────────────
        if card_type not in ("Visa", "Mastercard"):
            return {
                "success": False,
                "message": "Invalid card type. Only Visa and Mastercard are accepted.",
            }

        clean_number = card_number.replace(" ", "").replace("-", "")
        if not clean_number.isdigit() or len(clean_number) != 16:
            return {"success": False, "message": "Invalid card number format."}

        # Parse expiry → month / year
        expiry_parts = card_expiry.replace(" ", "").split("/")
        if len(expiry_parts) != 2 or not all(p.isdigit() for p in expiry_parts):
            return {
                "success": False,
                "message": "Invalid expiry date. Please use MM/YY format.",
            }
        expiry_month = int(expiry_parts[0])
        expiry_year = int(expiry_parts[1])
        # Convert 2-digit year to 4-digit
        if expiry_year < 100:
            expiry_year += 2000

        clean_cvc = card_cvc.replace(" ", "")
        if not clean_cvc.isdigit() or len(clean_cvc) not in (3, 4):
            return {"success": False, "message": "Invalid CVC code."}

        # ── Build WorldPay request ──────────────────────────────────────────
        transaction_ref = str(uuid.uuid4())
        amount_in_cents = int(round(amount * 100))

        payload = {
            "transactionReference": transaction_ref,
            "merchant": {
                "entity": WORLDPAY_MERCHANT_ENTITY,
            },
            "instruction": {
                "requestAutoSettlement": {
                    "enabled": True,
                },
                "narrative": {
                    "line1": description[:24],  # WorldPay limits to 24 chars
                },
                "value": {
                    "currency": "USD",
                    "amount": amount_in_cents,
                },
                "paymentInstrument": {
                    "type": "card/plain",
                    "cardNumber": clean_number,
                    "cardExpiryDate": {
                        "month": expiry_month,
                        "year": expiry_year,
                    },
                    "cvc": clean_cvc,
                },
            },
        }

        headers = {
            "Authorization": _basic_auth_header(),
            "Content-Type": API_VERSION,
            "Accept": API_VERSION,
        }

        url = f"{WORLDPAY_BASE_URL}/payments/authorizations"

        logger.info(
            f"WorldPay authorize request: {card_type} ending {clean_number[-4:]}, "
            f"${amount:.2f} (ref: {transaction_ref})"
        )

        # ── Call WorldPay API ───────────────────────────────────────────────
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=config.WORLDPAY_TIMEOUT)
            response_data = response.json() if response.content else {}
        except requests.exceptions.Timeout:
            logger.error("WorldPay API timeout")
            return {
                "success": False,
                "message": "Payment gateway timed out. Please try again.",
            }
        except requests.exceptions.ConnectionError as e:
            logger.error(f"WorldPay connection error: {e}")
            return {
                "success": False,
                "message": "Unable to reach payment gateway. Please try again later.",
            }
        except Exception as e:
            logger.error(f"WorldPay unexpected error: {e}")
            return {
                "success": False,
                "message": "An unexpected payment error occurred.",
            }

        logger.info(
            f"WorldPay response: HTTP {response.status_code} — "
            f"{response_data.get('outcome', 'no outcome')}"
        )

        # ── Parse response ──────────────────────────────────────────────────
        outcome = response_data.get("outcome", "")

        if response.status_code in (200, 201) and outcome == "authorized":
            return {
                "success": True,
                "transaction_id": transaction_ref,
                "amount": amount,
                "card_used": f"{card_type} ending in {clean_number[-4:]}",
                "message": "Payment authorized and settled successfully via WorldPay.",
                "worldpay_outcome": outcome,
                "risk_factors": response_data.get("riskFactors", []),
            }

        # Handle specific WorldPay decline / error outcomes
        error_message = self._extract_error_message(response.status_code, response_data)
        return {
            "success": False,
            "transaction_id": transaction_ref,
            "message": error_message,
            "worldpay_outcome": outcome,
        }

    @staticmethod
    def _extract_error_message(status_code: int, data: dict) -> str:
        """Turn WorldPay error responses into user-friendly messages."""
        if status_code == 401:
            return "Payment gateway authentication failed. Please contact support."
        if status_code == 400:
            validation_errors = data.get("validationErrors", [])
            if validation_errors:
                details = "; ".join(
                    e.get("message", e.get("errorName", "unknown"))
                    for e in validation_errors
                )
                return f"Payment validation error: {details}"
            return f"Payment request invalid: {data.get('message', 'unknown error')}"

        outcome = data.get("outcome", "")
        if outcome == "refused":
            return "Payment was declined by your card issuer. Please try a different card."
        if "error" in outcome.lower() if outcome else False:
            return f"Payment processing error: {outcome}"

        return f"Payment was not authorized (HTTP {status_code}). Please try again."


payment_service = PaymentService()
