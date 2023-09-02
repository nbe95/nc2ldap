"""Module for system-independent contact management."""

from dataclasses import dataclass
from typing import Optional, Tuple

from phonenumbers import PhoneNumber


@dataclass(frozen=True)
class Contact:
    """Contact structure for an independent and comparable base."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    address: Tuple[Optional[str], Optional[str]] = (None, None)
    email: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    phone_private: Optional[PhoneNumber] = None
    phone_mobile: Optional[PhoneNumber] = None
    phone_business1: Optional[PhoneNumber] = None
    phone_business2: Optional[PhoneNumber] = None

    def get_cn(self) -> str:
        """Build a CN based on this contact's data."""
        return f"{self.first_name or ''} {self.last_name or ''}".strip()

    def __repr__(self) -> str:
        """Generate a serialized representation for nice log output."""
        return f"{self.__class__.__name__}({self.get_cn()})"
