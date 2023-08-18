"""Module for system-independent contact management."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from phonenumbers import PhoneNumber, PhoneNumberFormat, format_number


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
    import_date: Optional[datetime] = None

    def get_cn(self) -> str:
        """Build a CN based on this contact's data."""
        return f"{self.first_name} {self.last_name}"

    def as_ldap_dict(self) -> Dict[str, str]:
        """Create a data record an LDAP server can handle."""

        def set_value(
            result: Dict[str, str], key: str, value: Optional[Any]
        ) -> None:
            """Add all set values to the result dictionary and format them."""
            if value is not None:
                parsed: str
                if isinstance(value, PhoneNumber):
                    parsed = format_number(
                        value, PhoneNumberFormat.INTERNATIONAL
                    )
                else:
                    parsed = value
                result.update({key: parsed})

        result: Dict[str, str] = {}
        set_value(result, "givenName", self.first_name)
        set_value(result, "sn", self.last_name)
        set_value(result, "telephoneNumber", self.phone_business1)
        set_value(result, "facsimileTelephoneNumber", self.phone_business2)
        set_value(result, "mobile", self.phone_mobile)
        set_value(result, "homePhone", self.phone_private)
        set_value(result, "o", self.company)
        set_value(result, "street", self.address[0])
        set_value(result, "l", self.address[1])
        set_value(result, "title", self.title)
        set_value(result, "mail", self.email)
        return result

    def __repr__(self) -> str:
        """Generate a serialized representation for nice log output."""
        return f"{self.__class__.__name__}({self.get_cn()})"
