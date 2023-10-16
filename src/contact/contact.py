"""Module for system-independent contact management."""

from dataclasses import dataclass
from typing import Optional, Tuple

from phonenumbers import FrozenPhoneNumber


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
        return " ".join(
            (v or "" for v in (self.title, self.first_name, self.last_name))
        ).strip()

    def __repr__(self) -> str:
        """Generate a serialized representation for nice log output."""
        return f"{self.__class__.__name__}({self.get_cn()})"
