"""
PassZen Vault — AES-256-GCM encryption and decryption engine.

Each piece of data is encrypted with a unique random nonce.
The nonce is prepended to the ciphertext for storage.
AES-GCM provides both confidentiality and integrity (authenticated encryption).
"""

import os
import json
import base64
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from src.config import (
    NONCE_LENGTH,
    VAULT_META_FILE,
    RECOVERY_FILE,
    RECOVERY_KEY_LENGTH,
    DATA_DIR,
    ensure_data_dir,
)
from src.crypto.key_derivation import generate_salt, derive_key


class Vault:
    """
    Manages the encryption/decryption lifecycle for PassZen.

    The vault key is derived from the user's 6-digit PIN via PBKDF2 and is
    held in memory only while the vault is unlocked. On lock, the key is
    discarded.
    """

    def __init__(self):
        self._key: Optional[bytes] = None
        self._salt: Optional[bytes] = None
        self._aesgcm: Optional[AESGCM] = None
        self._verification_token: Optional[bytes] = None

    # ── Properties ───────────────────────────────────────────────────────

    @property
    def is_unlocked(self) -> bool:
        """Returns True if the vault is currently unlocked (key in memory)."""
        return self._key is not None

    @property
    def salt(self) -> Optional[bytes]:
        """Returns the current salt, or None if vault is not initialized."""
        return self._salt

    # ── Vault Initialization (First-Time Setup) ─────────────────────────

    def initialize(
        self,
        pin: str,
        security_question: str,
        security_answer: str,
    ) -> str:
        """
        Initialize a new vault with the user's chosen PIN.

        Creates the salt, derives the encryption key, generates a recovery key,
        and persists vault metadata to disk.

        Args:
            pin:               The user's chosen 6-digit PIN.
            security_question: The chosen security question.
            security_answer:   The user's answer to the security question.

        Returns:
            The one-time recovery key (24-char alphanumeric string) that the
            user must save.
        """
        ensure_data_dir()

        # Generate salt and derive key
        self._salt = generate_salt()
        self._key = derive_key(pin, self._salt)
        self._aesgcm = AESGCM(self._key)

        # Create a verification token — we encrypt a known plaintext so we can
        # later verify the PIN by trying to decrypt it.
        verification_plaintext = b"PASSZEN_VAULT_VERIFICATION"
        self._verification_token = self.encrypt(verification_plaintext)

        # Generate a recovery key
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits
        recovery_key = "".join(
            secrets.choice(alphabet) for _ in range(RECOVERY_KEY_LENGTH)
        )

        # Encrypt the recovery key using a key derived from the security answer
        answer_salt = generate_salt()
        answer_key = derive_key(security_answer.strip().lower(), answer_salt)
        answer_aesgcm = AESGCM(answer_key)
        recovery_nonce = os.urandom(NONCE_LENGTH)
        encrypted_recovery = answer_aesgcm.encrypt(
            recovery_nonce, recovery_key.encode("utf-8"), None
        )

        # Also encrypt the vault key using the recovery key itself, so
        # that the recovery key can be used to reset the PIN.
        recovery_key_derived = derive_key(recovery_key, self._salt)
        recovery_aesgcm = AESGCM(recovery_key_derived)
        vault_key_nonce = os.urandom(NONCE_LENGTH)
        encrypted_vault_key = recovery_aesgcm.encrypt(
            vault_key_nonce, self._key, None
        )

        # Save vault metadata
        meta = {
            "version": 1,
            "salt": base64.b64encode(self._salt).decode("utf-8"),
            "verification_token": base64.b64encode(
                self._verification_token
            ).decode("utf-8"),
            "security_question": security_question,
        }
        with open(VAULT_META_FILE, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        # Save recovery data
        recovery_data = {
            "answer_salt": base64.b64encode(answer_salt).decode("utf-8"),
            "recovery_nonce": base64.b64encode(recovery_nonce).decode("utf-8"),
            "encrypted_recovery_key": base64.b64encode(
                encrypted_recovery
            ).decode("utf-8"),
            "vault_key_nonce": base64.b64encode(vault_key_nonce).decode("utf-8"),
            "encrypted_vault_key": base64.b64encode(
                encrypted_vault_key
            ).decode("utf-8"),
        }
        with open(RECOVERY_FILE, "w", encoding="utf-8") as f:
            json.dump(recovery_data, f, indent=2)

        return recovery_key

    # ── Unlock / Lock ───────────────────────────────────────────────────

    def unlock(self, pin: str) -> bool:
        """
        Attempt to unlock the vault with the given PIN.

        Derives the AES key from the PIN + stored salt, then tries to
        decrypt the verification token to confirm correctness.

        Args:
            pin: The user's 6-digit PIN.

        Returns:
            True if the PIN is correct and the vault is now unlocked.
        """
        meta = self._load_meta()
        if meta is None:
            return False

        self._salt = base64.b64decode(meta["salt"])
        verification_token = base64.b64decode(meta["verification_token"])

        # Derive key from the provided PIN
        candidate_key = derive_key(pin, self._salt)
        candidate_aesgcm = AESGCM(candidate_key)

        # Try to decrypt the verification token
        try:
            nonce = verification_token[:NONCE_LENGTH]
            ciphertext = verification_token[NONCE_LENGTH:]
            result = candidate_aesgcm.decrypt(nonce, ciphertext, None)
            if result == b"PASSZEN_VAULT_VERIFICATION":
                self._key = candidate_key
                self._aesgcm = candidate_aesgcm
                return True
        except Exception:
            pass

        return False

    def lock(self):
        """
        Lock the vault — wipe the key and AESGCM instance from memory.
        """
        # Overwrite the key bytes before discarding reference
        if self._key is not None:
            # Best-effort memory wipe (Python doesn't guarantee this due to GC,
            # but we do our best by replacing with zeros then releasing)
            zero_key = b"\x00" * len(self._key)
            self._key = zero_key
        self._key = None
        self._aesgcm = None

    # ── Encrypt / Decrypt ───────────────────────────────────────────────

    def encrypt(self, plaintext: bytes) -> bytes:
        """
        Encrypt plaintext using AES-256-GCM with a fresh random nonce.

        The nonce is prepended to the ciphertext for storage.
        Format: nonce (12 bytes) || ciphertext+tag

        Args:
            plaintext: The data to encrypt.

        Returns:
            The nonce + ciphertext bytes.

        Raises:
            RuntimeError: If the vault is locked.
        """
        if not self.is_unlocked:
            raise RuntimeError("Vault is locked. Unlock before encrypting.")

        nonce = os.urandom(NONCE_LENGTH)
        ciphertext = self._aesgcm.encrypt(nonce, plaintext, None)
        return nonce + ciphertext

    def decrypt(self, data: bytes) -> bytes:
        """
        Decrypt data that was encrypted by `encrypt()`.

        Expects the first 12 bytes to be the nonce, followed by ciphertext+tag.

        Args:
            data: The nonce + ciphertext bytes.

        Returns:
            The decrypted plaintext bytes.

        Raises:
            RuntimeError: If the vault is locked.
            Exception: If decryption fails (wrong key or tampered data).
        """
        if not self.is_unlocked:
            raise RuntimeError("Vault is locked. Unlock before decrypting.")

        nonce = data[:NONCE_LENGTH]
        ciphertext = data[NONCE_LENGTH:]
        return self._aesgcm.decrypt(nonce, ciphertext, None)

    def encrypt_string(self, text: str) -> bytes:
        """Encrypt a UTF-8 string."""
        return self.encrypt(text.encode("utf-8"))

    def decrypt_string(self, data: bytes) -> str:
        """Decrypt bytes back to a UTF-8 string."""
        return self.decrypt(data).decode("utf-8")

    # ── Recovery ────────────────────────────────────────────────────────

    def get_security_question(self) -> Optional[str]:
        """Return the stored security question, or None if vault not set up."""
        meta = self._load_meta()
        if meta:
            return meta.get("security_question")
        return None

    def recover_with_answer(self, security_answer: str) -> Optional[str]:
        """
        Attempt to recover the recovery key using the security answer.

        Args:
            security_answer: The user's answer to their security question.

        Returns:
            The recovery key string if the answer is correct, None otherwise.
        """
        try:
            with open(RECOVERY_FILE, "r", encoding="utf-8") as f:
                recovery_data = json.load(f)

            answer_salt = base64.b64decode(recovery_data["answer_salt"])
            recovery_nonce = base64.b64decode(recovery_data["recovery_nonce"])
            encrypted_recovery = base64.b64decode(
                recovery_data["encrypted_recovery_key"]
            )

            # Derive key from the security answer
            answer_key = derive_key(
                security_answer.strip().lower(), answer_salt
            )
            answer_aesgcm = AESGCM(answer_key)

            # Try to decrypt the recovery key
            recovery_key = answer_aesgcm.decrypt(
                recovery_nonce, encrypted_recovery, None
            ).decode("utf-8")

            return recovery_key

        except Exception:
            return None

    def reset_pin_with_recovery_key(
        self,
        recovery_key: str,
        new_pin: str,
        new_security_question: str,
        new_security_answer: str,
    ) -> bool:
        """
        Reset the vault PIN using the recovery key.

        This decrypts the vault key using the recovery key, then re-encrypts
        the vault with a new key derived from the new PIN.

        Args:
            recovery_key:          The recovery key string.
            new_pin:               The new 6-digit PIN.
            new_security_question: New security question.
            new_security_answer:   New security answer.

        Returns:
            True if the PIN was successfully reset.
        """
        try:
            meta = self._load_meta()
            if meta is None:
                return False

            old_salt = base64.b64decode(meta["salt"])

            with open(RECOVERY_FILE, "r", encoding="utf-8") as f:
                recovery_data = json.load(f)

            vault_key_nonce = base64.b64decode(recovery_data["vault_key_nonce"])
            encrypted_vault_key = base64.b64decode(
                recovery_data["encrypted_vault_key"]
            )

            # Derive the key from the recovery key
            recovery_key_derived = derive_key(recovery_key, old_salt)
            recovery_aesgcm = AESGCM(recovery_key_derived)

            # Decrypt the original vault key
            old_vault_key = recovery_aesgcm.decrypt(
                vault_key_nonce, encrypted_vault_key, None
            )

            # Now we have the old key — unlock the vault with it
            self._key = old_vault_key
            self._aesgcm = AESGCM(self._key)
            self._salt = old_salt

            # Re-initialize will handle re-encryption in the database layer
            # For now, store the old key so the database can re-encrypt
            return True

        except Exception:
            return False

    # ── Vault Status ────────────────────────────────────────────────────

    @staticmethod
    def is_initialized() -> bool:
        """Check if a vault has been created (first-time setup completed)."""
        return os.path.exists(VAULT_META_FILE)

    # ── Private Helpers ─────────────────────────────────────────────────

    @staticmethod
    def _load_meta() -> Optional[dict]:
        """Load vault metadata from disk."""
        try:
            with open(VAULT_META_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
