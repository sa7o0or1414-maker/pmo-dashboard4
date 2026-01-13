import os
import base64
import hashlib
import hmac


def hash_password(password: str, salt: bytes | None = None, iterations: int = 200_000) -> str:
    """
    Returns a compact string: base64(salt)$base64(hash)$iterations
    """
    if salt is None:
        salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations, dklen=32)
    return f"{base64.b64encode(salt).decode()}${base64.b64encode(dk).decode()}${iterations}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_b64, dk_b64, it_str = stored.split("$")
        salt = base64.b64decode(salt_b64.encode())
        dk_expected = base64.b64decode(dk_b64.encode())
        iterations = int(it_str)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations, dklen=32)
        return hmac.compare_digest(dk, dk_expected)
    except Exception:
        return False
