"""Module for system-independent contact management."""

import logging
from dataclasses import dataclass
from typing import List, Optional, Tuple
from uuid import uuid4

from phonenumbers import FrozenPhoneNumber

from nc2ldap.constants import LOG_LEVEL

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)


@dataclass(frozen=True, eq=True)
class Contact:
    """Contact structure for an independent and comparable base."""

    first_name: Optional[str] = None
    last_name: str = ""
    address: Tuple[Optional[str], Optional[str]] = (None, None)
    email: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    phone_private: Optional[FrozenPhoneNumber] = None
    phone_mobile: Optional[FrozenPhoneNumber] = None
    phone_business1: Optional[FrozenPhoneNumber] = None
    phone_business2: Optional[FrozenPhoneNumber] = None

    def get_cn(self) -> str:
        """Build a CN based on this contact's data (full name or company)."""
        fields: List[Optional[str]] = [
            self.title,
            self.first_name,
            self.last_name,
            f"({self.company})" if self.company else None,
        ]
        result: str = " ".join(v for v in fields if v).strip()
        return result or str(uuid4())  # Always return a non-empty string!

    def __repr__(self) -> str:
        """Generate a serialized representation for nice log output."""
        return f"{self.__class__.__name__}({self.get_cn()})"
