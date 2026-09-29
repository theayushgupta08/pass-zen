"""
PassZen Export/Import — Encrypted .passzen file format for vault portability.

The export file contains:
- Format version
- The salt (so the same PIN can derive the same key on another machine)
- All entries (encrypted with the vault key)

The file is a JSON structure with base64-encoded encrypted blobs.
"""

import json
import base64
import os
from typing import List, Tuple, Optional
from datetime import datetime

from src.config import EXPORT_FORMAT_VERSION, EXPORT_FILE_EXTENSION
from src.crypto.vault import Vault
from src.crypto.key_derivation import derive_key
from src.models.entry import PasswordEntry

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def export_vault(
    entries: List[PasswordEntry],
    vault: Vault,
    filepath: str,
):
    """
    Export all entries to an encrypted .passzen file.

    The file embeds the salt so it can be imported on another machine
    using the same PIN.

    Args:
        entries:  List of decrypted PasswordEntry objects.
        vault:    The unlocked Vault instance.
        filepath: Destination file path.
    """
    if not filepath.endswith(EXPORT_FILE_EXTENSION):
        filepath += EXPORT_FILE_EXTENSION

    # Serialize entries to JSON, then encrypt the whole blob
    entries_data = [
        {
            "id": e.id,
            "website": e.website,
            "username": e.username,
            "password": e.password,
            "category": e.category,
            "created_at": e.created_at,
            "updated_at": e.updated_at,
        }
        for e in entries
    ]

    plaintext = json.dumps(entries_data, indent=2).encode("utf-8")
    encrypted_blob = vault.encrypt(plaintext)

    export_data = {
        "format": "passzen",
        "version": EXPORT_FORMAT_VERSION,
        "salt": base64.b64encode(vault.salt).decode("utf-8"),
        "exported_at": datetime.now().isoformat(),
        "entry_count": len(entries),
        "data": base64.b64encode(encrypted_blob).decode("utf-8"),
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2)


def import_vault(
    filepath: str,
    source_pin: str,
) -> Tuple[Optional[List[PasswordEntry]], Optional[str]]:
    """
    Import entries from an encrypted .passzen file.

    The user must provide the PIN that was used on the source machine.
    The salt embedded in the file is used to derive the same key.

    Args:
        filepath:   Path to the .passzen file.
        source_pin: The PIN used on the source machine.

    Returns:
        A tuple of (list of PasswordEntry, error_message).
        On success, error_message is None.
        On failure, list is None and error_message describes the problem.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            export_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return None, f"Could not read file: {e}"

    # Validate format
    if export_data.get("format") != "passzen":
        return None, "Invalid file format. This is not a PassZen export."

    version = export_data.get("version", 0)
    if version > EXPORT_FORMAT_VERSION:
        return None, (
            f"This file was created with a newer version of PassZen "
            f"(v{version}). Please update the app."
        )

    try:
        salt = base64.b64decode(export_data["salt"])
        encrypted_blob = base64.b64decode(export_data["data"])
    except (KeyError, Exception) as e:
        return None, f"Corrupted export file: {e}"

    # Derive the key from the source PIN + embedded salt
    try:
        key = derive_key(source_pin, salt)
        aesgcm = AESGCM(key)

        # Decrypt: first 12 bytes are nonce, rest is ciphertext
        from src.config import NONCE_LENGTH
        nonce = encrypted_blob[:NONCE_LENGTH]
        ciphertext = encrypted_blob[NONCE_LENGTH:]
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)

    except Exception:
        return None, "Incorrect PIN. Could not decrypt the export file."

    # Parse the decrypted JSON
    try:
        entries_data = json.loads(plaintext.decode("utf-8"))
        entries = [
            PasswordEntry(
                id=e["id"],
                website=e["website"],
                username=e["username"],
                password=e["password"],
                category=e.get("category", "Other"),
                created_at=e.get("created_at", datetime.now().isoformat()),
                updated_at=e.get("updated_at", datetime.now().isoformat()),
            )
            for e in entries_data
        ]
        return entries, None

    except (json.JSONDecodeError, KeyError) as e:
        return None, f"Corrupted entry data: {e}"


def find_duplicates(
    existing: List[PasswordEntry],
    imported: List[PasswordEntry],
) -> Tuple[List[PasswordEntry], List[PasswordEntry]]:
    """
    Identify duplicates between existing and imported entries.

    A duplicate is defined as matching website + username (case-insensitive).

    Args:
        existing: Current vault entries.
        imported: Entries from the import file.

    Returns:
        A tuple of (unique_new_entries, duplicate_entries).
    """
    existing_keys = {
        (e.website.lower(), e.username.lower()) for e in existing
    }

    unique = []
    duplicates = []

    for entry in imported:
        key = (entry.website.lower(), entry.username.lower())
        if key in existing_keys:
            duplicates.append(entry)
        else:
            unique.append(entry)

    return unique, duplicates
