"""Module contact conversion functions."""

from typing import Any, Dict, List, Optional, Type, Union

from phonenumbers import PhoneNumber, PhoneNumberFormat, format_number, parse
from phonenumbers.phonenumberutil import NumberParseException

from .contact import Contact


def contact_to_ldap_dict(contact: Contact) -> Dict[str, str]:
    """Create a data record an LDAP server can handle."""

    def set_value(
        result: Dict[str, str], key: str, value: Optional[Any]
    ) -> None:
        """Add all set values to the result dictionary and format them."""
        if value is not None:
            parsed: str
            if isinstance(value, PhoneNumber):
                parsed = format_number(value, PhoneNumberFormat.INTERNATIONAL)
            else:
                parsed = value
            result.update({key: parsed})

    result: Dict[str, str] = {}
    set_value(result, "givenName", contact.first_name)
    set_value(result, "sn", contact.last_name)
    set_value(result, "telephoneNumber", contact.phone_business1)
    set_value(result, "facsimileTelephoneNumber", contact.phone_business2)
    set_value(result, "mobile", contact.phone_mobile)
    set_value(result, "homePhone", contact.phone_private)
    set_value(result, "o", contact.company)
    set_value(result, "street", contact.address[0])
    set_value(result, "l", contact.address[1])
    set_value(result, "title", contact.title)
    set_value(result, "mail", contact.email)
    return result


def contact_from_ldap_dict(data: Dict[str, Any]) -> Contact:
    """Create a contact based on data from an LDAP server."""

    def get_field(
        attr: Dict[str, Any], key: str, value_type: Type[Any] = str
    ) -> Optional[Any]:
        """Fetch/cast an LDAP attribute, which might be wrapped in a list."""
        wrapper_or_value: Optional[Union[List[Any], Any]] = attr.get(key)
        if wrapper_or_value is None:
            return None

        value: Any = (
            wrapper_or_value
            if not isinstance(wrapper_or_value, list)
            else wrapper_or_value[0]
        )
        if value_type == PhoneNumber:
            try:
                return parse(value)
            except NumberParseException:
                return None
        return value

    return Contact(
        get_field(data, "givenName"),
        get_field(data, "sn"),
        (get_field(data, "street"), get_field(data, "l")),
        get_field(data, "mail"),
        get_field(data, "o"),
        get_field(data, "title"),
        get_field(data, "homePhone", PhoneNumber),
        get_field(data, "mobile", PhoneNumber),
        get_field(data, "telephoneNumber", PhoneNumber),
        get_field(data, "facsimileTelephoneNumber", PhoneNumber),
        data.get("createTimestamp"),
    )
