"""
PassZen Database — SQLite CRUD operations with encrypted fields.

All sensitive fields (website, username, password) are encrypted individually
by the Vault before being stored. The category field is stored in plaintext
to allow efficient filtering.
"""

import sqlite3
import base64
from typing import List, Optional

from src.config import VAULT_DB_FILE, PREDEFINED_CATEGORIES, ensure_data_dir
from src.crypto.vault import Vault
from src.models.entry import PasswordEntry, Category


class Database:
    """
    Manages the SQLite database for PassZen.

    All read/write operations for password entries go through this class.
    Sensitive fields are encrypted/decrypted via the provided Vault instance.
    """

    def __init__(self, vault: Vault):
        self._vault = vault
        self._conn: Optional[sqlite3.Connection] = None

    # ── Connection Management ────────────────────────────────────────────

    def connect(self):
        """Open a connection to the SQLite database and ensure tables exist."""
        ensure_data_dir()
        self._conn = sqlite3.connect(VAULT_DB_FILE)
        self._conn.row_factory = sqlite3.Row
        self._create_tables()

    def close(self):
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    # ── Schema ───────────────────────────────────────────────────────────

    def _create_tables(self):
        """Create the entries and categories tables if they don't exist."""
        cursor = self._conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id          TEXT PRIMARY KEY,
                website     TEXT NOT NULL,
                username    TEXT NOT NULL,
                password    TEXT NOT NULL,
                category    TEXT DEFAULT 'Other',
                created_at  TEXT NOT NULL,
                updated_at  TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id          TEXT PRIMARY KEY,
                name        TEXT NOT NULL UNIQUE,
                is_custom   INTEGER DEFAULT 0,
                created_at  TEXT NOT NULL
            )
        """)

        self._conn.commit()

        # Seed predefined categories
        self._seed_categories()

    def _seed_categories(self):
        """Insert predefined categories if they don't already exist."""
        cursor = self._conn.cursor()
        from datetime import datetime

        for name in PREDEFINED_CATEGORIES:
            try:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO categories (id, name, is_custom, created_at)
                    VALUES (?, ?, 0, ?)
                    """,
                    (
                        str(__import__("uuid").uuid4()),
                        name,
                        datetime.now().isoformat(),
                    ),
                )
            except sqlite3.IntegrityError:
                pass

        self._conn.commit()

    # ── Entry CRUD ───────────────────────────────────────────────────────

    def add_entry(self, entry: PasswordEntry) -> str:
        """
        Add a new password entry to the database.

        Encrypts the website, username, and password fields before storing.

        Args:
            entry: The PasswordEntry to add.

        Returns:
            The ID of the newly created entry.
        """
        encrypted_website = base64.b64encode(
            self._vault.encrypt_string(entry.website)
        ).decode("utf-8")
        encrypted_username = base64.b64encode(
            self._vault.encrypt_string(entry.username)
        ).decode("utf-8")
        encrypted_password = base64.b64encode(
            self._vault.encrypt_string(entry.password)
        ).decode("utf-8")

        cursor = self._conn.cursor()
        cursor.execute(
            """
            INSERT INTO entries (id, website, username, password, category,
                                 created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry.id,
                encrypted_website,
                encrypted_username,
                encrypted_password,
                entry.category,
                entry.created_at,
                entry.updated_at,
            ),
        )
        self._conn.commit()
        return entry.id

    def get_all_entries(self) -> List[PasswordEntry]:
        """
        Retrieve and decrypt all password entries.

        Returns:
            A list of PasswordEntry objects with decrypted fields.
        """
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT * FROM entries ORDER BY updated_at DESC"
        )
        rows = cursor.fetchall()

        entries = []
        for row in rows:
            try:
                entry = PasswordEntry(
                    id=row["id"],
                    website=self._vault.decrypt_string(
                        base64.b64decode(row["website"])
                    ),
                    username=self._vault.decrypt_string(
                        base64.b64decode(row["username"])
                    ),
                    password=self._vault.decrypt_string(
                        base64.b64decode(row["password"])
                    ),
                    category=row["category"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
                entries.append(entry)
            except Exception:
                # Skip entries that can't be decrypted (shouldn't happen
                # under normal circumstances)
                continue

        return entries

    def get_entry_by_id(self, entry_id: str) -> Optional[PasswordEntry]:
        """
        Retrieve a single entry by its ID.

        Args:
            entry_id: The UUID of the entry to retrieve.

        Returns:
            A PasswordEntry with decrypted fields, or None if not found.
        """
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        try:
            return PasswordEntry(
                id=row["id"],
                website=self._vault.decrypt_string(
                    base64.b64decode(row["website"])
                ),
                username=self._vault.decrypt_string(
                    base64.b64decode(row["username"])
                ),
                password=self._vault.decrypt_string(
                    base64.b64decode(row["password"])
                ),
                category=row["category"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
        except Exception:
            return None

    def update_entry(self, entry: PasswordEntry):
        """
        Update an existing entry with new values.

        Args:
            entry: The PasswordEntry with updated fields.
        """
        entry.touch()

        encrypted_website = base64.b64encode(
            self._vault.encrypt_string(entry.website)
        ).decode("utf-8")
        encrypted_username = base64.b64encode(
            self._vault.encrypt_string(entry.username)
        ).decode("utf-8")
        encrypted_password = base64.b64encode(
            self._vault.encrypt_string(entry.password)
        ).decode("utf-8")

        cursor = self._conn.cursor()
        cursor.execute(
            """
            UPDATE entries
            SET website = ?, username = ?, password = ?, category = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                encrypted_website,
                encrypted_username,
                encrypted_password,
                entry.category,
                entry.updated_at,
                entry.id,
            ),
        )
        self._conn.commit()

    def delete_entry(self, entry_id: str):
        """
        Delete an entry by its ID.

        Args:
            entry_id: The UUID of the entry to delete.
        """
        cursor = self._conn.cursor()
        cursor.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
        self._conn.commit()

    def search_entries(
        self, query: str, category: Optional[str] = None
    ) -> List[PasswordEntry]:
        """
        Search entries by decrypted website/username matching a query.

        Since the fields are encrypted, we must decrypt all entries first
        and then filter in Python.

        Args:
            query:    The search string (case-insensitive).
            category: Optional category filter.

        Returns:
            A filtered list of PasswordEntry objects.
        """
        all_entries = self.get_all_entries()
        query_lower = query.lower().strip()

        results = []
        for entry in all_entries:
            # Filter by category first (plaintext, cheap check)
            if category and category != "All" and entry.category != category:
                continue

            # Then filter by search query
            if query_lower:
                if (
                    query_lower in entry.website.lower()
                    or query_lower in entry.username.lower()
                ):
                    results.append(entry)
            else:
                results.append(entry)

        return results

    def get_entry_count(self) -> int:
        """Return the total number of entries in the vault."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM entries")
        return cursor.fetchone()[0]

    # ── Category CRUD ────────────────────────────────────────────────────

    def get_all_categories(self) -> List[Category]:
        """Retrieve all categories (predefined + custom)."""
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT * FROM categories ORDER BY is_custom ASC, name ASC"
        )
        rows = cursor.fetchall()

        return [
            Category(
                id=row["id"],
                name=row["name"],
                is_custom=bool(row["is_custom"]),
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def add_category(self, name: str) -> Optional[str]:
        """
        Add a custom category.

        Args:
            name: The category name.

        Returns:
            The category ID, or None if the name already exists.
        """
        from datetime import datetime
        import uuid

        cat = Category(
            id=str(uuid.uuid4()),
            name=name.strip(),
            is_custom=True,
            created_at=datetime.now().isoformat(),
        )

        try:
            cursor = self._conn.cursor()
            cursor.execute(
                """
                INSERT INTO categories (id, name, is_custom, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (cat.id, cat.name, 1, cat.created_at),
            )
            self._conn.commit()
            return cat.id
        except sqlite3.IntegrityError:
            return None

    def delete_category(self, category_id: str):
        """
        Delete a custom category.

        Entries with this category will be reassigned to "Other".

        Args:
            category_id: The UUID of the category to delete.
        """
        cursor = self._conn.cursor()

        # Get the category name before deletion
        cursor.execute(
            "SELECT name FROM categories WHERE id = ? AND is_custom = 1",
            (category_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return  # Can't delete predefined categories

        category_name = row["name"]

        # Reassign entries to "Other"
        cursor.execute(
            "UPDATE entries SET category = 'Other' WHERE category = ?",
            (category_name,),
        )

        # Delete the category
        cursor.execute(
            "DELETE FROM categories WHERE id = ?", (category_id,)
        )
        self._conn.commit()

    # ── Re-encryption (for PIN change) ──────────────────────────────────

    def re_encrypt_all_entries(self, old_vault: Vault, new_vault: Vault):
        """
        Re-encrypt all entries with a new vault key.

        Used when the user changes their PIN. Decrypts everything with the
        old key and re-encrypts with the new key.

        Args:
            old_vault: The Vault instance with the old key.
            new_vault: The Vault instance with the new key.
        """
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM entries")
        rows = cursor.fetchall()

        for row in rows:
            try:
                # Decrypt with old key
                website = old_vault.decrypt_string(
                    base64.b64decode(row["website"])
                )
                username = old_vault.decrypt_string(
                    base64.b64decode(row["username"])
                )
                password = old_vault.decrypt_string(
                    base64.b64decode(row["password"])
                )

                # Re-encrypt with new key
                new_website = base64.b64encode(
                    new_vault.encrypt_string(website)
                ).decode("utf-8")
                new_username = base64.b64encode(
                    new_vault.encrypt_string(username)
                ).decode("utf-8")
                new_password = base64.b64encode(
                    new_vault.encrypt_string(password)
                ).decode("utf-8")

                cursor.execute(
                    """
                    UPDATE entries
                    SET website = ?, username = ?, password = ?
                    WHERE id = ?
                    """,
                    (new_website, new_username, new_password, row["id"]),
                )
            except Exception:
                continue

        self._conn.commit()
