import decimal
import logging

import razorpay
from django.conf import settings

logger = logging.getLogger(__name__)


def _get_client() -> razorpay.Client:
    """
    Initialize and return a Razorpay client using credentials from settings.
    """
    key_id = getattr(settings, "RAZORPAY_KEY_ID", None)
    key_secret = getattr(settings, "RAZORPAY_KEY_SECRET", None)

    if not key_id or not key_secret:
        logger.error("Razorpay credentials missing: RAZORPAY_KEY_ID or RAZORPAY_KEY_SECRET not set")
        raise RuntimeError(
            "Razorpay credentials are not configured. "
            "Please set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in environment."
        )

    # Log presence of key (masked) for easier debugging in dev without exposing secret
    try:
        masked = f"{key_id[:6]}...{key_id[-4:]}" if len(key_id) > 10 else key_id
    except Exception:
        masked = "(invalid-key)"
    logger.debug("Initializing Razorpay client using key id: %s", masked)

    return razorpay.Client(auth=(key_id, key_secret))


def create_order(amount, currency: str = "INR") -> dict:
    """
    Create a Razorpay order.

    - `amount` is expected in rupees (Decimal / float).
    - Razorpay expects amount in paise (integer).
    """
    if isinstance(amount, decimal.Decimal):
        amount = float(amount)

    amount_paise = int(round(amount * 100))

    client = _get_client()
    payload = {
        "amount": amount_paise,
        "currency": currency,
    }
    return client.order.create(payload)


def verify_payment_signature(razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str) -> bool:
    """
    Verify Razorpay payment signature.

    Returns True if valid, raises razorpay.errors.SignatureVerificationError if invalid.
    """
    client = _get_client()
    params_dict = {
        "razorpay_order_id": razorpay_order_id,
        "razorpay_payment_id": razorpay_payment_id,
        "razorpay_signature": razorpay_signature,
    }
    client.utility.verify_payment_signature(params_dict)
    return True


