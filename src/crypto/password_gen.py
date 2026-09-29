"""
PassZen Password Generator — Cryptographically secure password generation.

Uses Python's `secrets` module for CSPRNG. Guarantees at least one character
from each enabled pool, then fills remaining length from the combined pool.
"""

import secrets
import string
import re
from typing import Optional

from src.config import (
    CHARACTER_POOLS,
    DEFAULT_PASSWORD_LENGTH,
    MIN_PASSWORD_LENGTH,
    MAX_PASSWORD_LENGTH,
)


def generate_password(
    length: int = DEFAULT_PASSWORD_LENGTH,
    use_uppercase: bool = True,
    use_lowercase: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
) -> str:
    """
    Generate a cryptographically secure random password.

    Guarantees at least one character from each enabled pool. Rejects
    passwords with 3+ consecutive repeated characters or sequential runs.

    Args:
        length:        Desired password length (clamped to 8–64).
        use_uppercase: Include uppercase letters.
        use_lowercase: Include lowercase letters.
        use_digits:    Include digits.
        use_symbols:   Include symbols.

    Returns:
        A randomly generated password string.

    Raises:
        ValueError: If no character pools are enabled.
    """
    length = max(MIN_PASSWORD_LENGTH, min(length, MAX_PASSWORD_LENGTH))

    # Build the set of enabled pools
    enabled_pools = []
    if use_uppercase:
        enabled_pools.append(CHARACTER_POOLS["uppercase"])
    if use_lowercase:
        enabled_pools.append(CHARACTER_POOLS["lowercase"])
    if use_digits:
        enabled_pools.append(CHARACTER_POOLS["digits"])
    if use_symbols:
        enabled_pools.append(CHARACTER_POOLS["symbols"])

    if not enabled_pools:
        raise ValueError("At least one character pool must be enabled.")

    # Ensure length is at least the number of enabled pools (to guarantee
    # at least one from each)
    if length < len(enabled_pools):
        length = len(enabled_pools)

    # Generate candidates until we get one that passes quality checks
    combined_pool = "".join(enabled_pools)

    for _ in range(100):  # Max retries to avoid infinite loop
        # Start with one guaranteed character from each enabled pool
        password_chars = [secrets.choice(pool) for pool in enabled_pools]

        # Fill the remaining length from the combined pool
        remaining = length - len(password_chars)
        for _ in range(remaining):
            password_chars.append(secrets.choice(combined_pool))

        # Shuffle to avoid predictable positions (first chars from each pool)
        secrets.SystemRandom().shuffle(password_chars)
        password = "".join(password_chars)

        # Quality check: reject bad patterns
        if _passes_quality_check(password):
            return password

    # Fallback: return the last generated password even if it didn't pass
    # quality checks (extremely unlikely to reach here)
    return password


def calculate_strength(password: str) -> dict:
    """
    Calculate the strength of a password.

    Returns a dict with:
        - score:  Integer 0–9
        - rating: One of "Weak", "Fair", "Strong", "Very Strong"
        - color:  Color hex for the UI meter
        - details: List of criteria met/unmet

    Args:
        password: The password to evaluate.

    Returns:
        Strength assessment dictionary.
    """
    if not password:
        return {
            "score": 0,
            "rating": "Weak",
            "color": "#FF4757",
            "details": [],
        }

    score = 0
    details = []

    # Length checks
    if len(password) >= 8:
        score += 1
        details.append("✅ At least 8 characters")
    else:
        details.append("❌ Less than 8 characters")

    if len(password) >= 12:
        score += 1
        details.append("✅ At least 12 characters")

    if len(password) >= 16:
        score += 1
        details.append("✅ At least 16 characters")

    # Character diversity
    if re.search(r"[A-Z]", password):
        score += 1
        details.append("✅ Contains uppercase")
    else:
        details.append("❌ No uppercase letters")

    if re.search(r"[a-z]", password):
        score += 1
        details.append("✅ Contains lowercase")
    else:
        details.append("❌ No lowercase letters")

    if re.search(r"[0-9]", password):
        score += 1
        details.append("✅ Contains digits")
    else:
        details.append("❌ No digits")

    if re.search(r"[^A-Za-z0-9]", password):
        score += 1
        details.append("✅ Contains symbols")
    else:
        details.append("❌ No symbols")

    # Pattern checks
    if not re.search(r"(.)\1{2,}", password):
        score += 1
        details.append("✅ No repeated characters (3+)")
    else:
        details.append("❌ Contains repeated characters")

    if not _has_sequential_pattern(password):
        score += 1
        details.append("✅ No sequential patterns")
    else:
        details.append("❌ Contains sequential patterns")

    # Map score to rating
    if score <= 3:
        rating = "Weak"
        color = "#FF4757"
    elif score <= 5:
        rating = "Fair"
        color = "#FFA502"
    elif score <= 7:
        rating = "Strong"
        color = "#2ED573"
    else:
        rating = "Very Strong"
        color = "#6C63FF"

    return {
        "score": score,
        "rating": rating,
        "color": color,
        "details": details,
    }


# ── Private Helpers ──────────────────────────────────────────────────────────


def _passes_quality_check(password: str) -> bool:
    """
    Check that a generated password doesn't have obvious bad patterns.

    Rejects passwords with:
    - 3+ consecutive identical characters (e.g., "aaa")
    - 4+ sequential ascending/descending characters (e.g., "abcd", "4321")
    """
    # Check for 3+ repeated characters
    if re.search(r"(.)\1{2,}", password):
        return False

    # Check for sequential patterns
    if _has_sequential_pattern(password):
        return False

    return True


def _has_sequential_pattern(password: str, run_length: int = 4) -> bool:
    """
    Detect sequential ascending or descending runs of `run_length` or more.
    Works on character ordinal values (e.g., a-b-c-d or 1-2-3-4).
    """
    if len(password) < run_length:
        return False

    ascending = 1
    descending = 1

    for i in range(1, len(password)):
        diff = ord(password[i]) - ord(password[i - 1])

        if diff == 1:
            ascending += 1
            descending = 1
        elif diff == -1:
            descending += 1
            ascending = 1
        else:
            ascending = 1
            descending = 1

        if ascending >= run_length or descending >= run_length:
            return True

    return False
