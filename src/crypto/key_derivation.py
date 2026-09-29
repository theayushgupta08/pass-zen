"""
PassZen Key Derivation — PBKDF2-HMAC-SHA256 to derive AES-256 key from 6-digit PIN.
"""

import os
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

from src.config import PBKDF2_ITERATIONS, SALT_LENGTH, AES_KEY_LENGTH


def generate_salt() -> bytes:
    """Generate a cryptographically secure random salt."""
    return os.urandom(SALT_LENGTH)


def derive_key(pin: str, salt: bytes) -> bytes:
    """
    Derive a 256-bit AES key from a 6-digit PIN using PBKDF2-HMAC-SHA256.

    Args:
        pin:  The user's 6-digit PIN as a string (e.g. "123456").
        salt: A random 32-byte salt.

    Returns:
        A 32-byte (256-bit) derived key suitable for AES-256-GCM.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=AES_KEY_LENGTH,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(pin.encode("utf-8"))


def verify_pin(pin: str, salt: bytes, expected_key: bytes) -> bool:
    """
    Verify whether a given PIN produces the expected derived key.

    Args:
        pin:          The PIN to verify.
        salt:         The salt used during original key derivation.
        expected_key: The previously derived key to compare against.

    Returns:
        True if the PIN is correct, False otherwise.
    """
    try:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=AES_KEY_LENGTH,
            salt=salt,
            iterations=PBKDF2_ITERATIONS,
        )
        kdf.verify(pin.encode("utf-8"), expected_key)
        return True
    except Exception:
        return False
