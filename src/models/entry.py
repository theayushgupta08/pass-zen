"""
PassZen Models — Data classes for password entries and categories.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class PasswordEntry:
    """Represents a single password entry in the vault."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    website: str = ""
    username: str = ""
    password: str = ""
    category: str = "Other"
    created_at: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )

    def touch(self):
        """Update the `updated_at` timestamp to now."""
        self.updated_at = datetime.now().isoformat()


@dataclass
class Category:
    """Represents a category/tag for organizing entries."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    is_custom: bool = False
    created_at: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )
