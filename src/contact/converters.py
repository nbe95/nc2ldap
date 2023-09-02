"""Module contact conversion functions."""

import logging
from os import environ as env
from typing import Any, Callable, Dict, Iterable, List, Optional, Type, Union

from phonenumbers import (
    FrozenPhoneNumber,
    PhoneNumberFormat,
    format_number,
    parse,
)
from phonenumbers.phonenumberutil import NumberParseException
from vobject.base import Component
from vobject.vcard import Address

from .contact import Contact

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if "DEBUG" in env else logging.INFO)


def contact_to_ldap_dict(contact: Contact) -> Dict[str, str]:
    """Create a data record an LDAP server can handle."""

    def set_value(
        result: Dict[str, str], key: str, value: Optional[Any]
    ) -> None:
        """Add all set values to the result dictionary and format them."""
        if value is not None:
            parsed: str
            if isinstance(value, FrozenPhoneNumber):
                parsed = format_number(value, PhoneNumberFormat.INTERNATIONAL)
            else:
                parsed = value
            result.update({key: parsed})

    result: Dict[str, str] = {}
    set_value(result, "givenName", contact.first_name)
    set_value(result, "sn", contact.last_name or " ")   # not optional
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

        # Extract value if wrapped in a list
        value: Any = wrapper_or_value
        if isinstance(wrapper_or_value, list):
            if len(wrapper_or_value) > 1:
                logger.error(
                    "LDAP key '%s' contains more than one value to extract.",
                    key,
                )
            value = wrapper_or_value[0]

        if value_type == FrozenPhoneNumber:
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
        get_field(data, "homePhone", FrozenPhoneNumber),
        get_field(data, "mobile", FrozenPhoneNumber),
        get_field(data, "telephoneNumber", FrozenPhoneNumber),
        get_field(data, "facsimileTelephoneNumber", FrozenPhoneNumber),
    )


def contact_from_vcard(vcard: Component) -> Contact:
    """Fetch contact data from a vCard data structure."""

    def get_field(
        vcard: Component,
        key: str,
        filter_func: Optional[Callable[[Component], bool]] = None,
    ) -> Any:
        """Extract a single value from a specific field matching criteria."""
        items: List[Any] = vcard.contents.get(key, [])
        if not items:
            logger.debug(
                "Key '%s' not available in vCard for %s.", key, vcard.fn.value
            )
            return None

        if len(items) == 1:
            logger.debug(
                "Found unique key '%s' in vCard for %s.", key, vcard.fn.value
            )
            return items[0].value

        # Filter multiple available values
        if filter_func is None:
            logger.warning(
                "Returning first of multiple available values for key '%s' in "
                "vCard for %s.",
                key,
                vcard.fn.value,
            )
            return items[0].value

        filtered_items: List[Any] = list(filter(filter_func, items))
        if not filtered_items:
            logger.error(
                "No filter results for key '%s' in vCard for %s.",
                key,
                vcard.fn.value,
            )
            return None

        if len(filtered_items) > 1:
            logger.warning(
                "Multiple filter results for key '%s' in vCard for %s.",
                key,
                vcard.fn.value,
            )
        return filtered_items[0].value

    def is_type(component: Component, types: Iterable[str]) -> bool:
        # Catch argument without type specification (e.g. a phone number of
        # type "Notfall")
        if not component.params:
            return False
        return all(
            type_str.lower() in (t.lower() for t in component.type_paramlist)
            for type_str in types
        )

    first_name: Optional[str] = vcard.n.value.given or None
    # Note: The 'sn' attribute is not optional
    last_name: str = (
        vcard.n.value.family
        if not isinstance(vcard.n.value.family, list)
        else ", ".join(str(n).strip() for n in vcard.n.value.family)
    )
    title: Optional[str] = vcard.n.value.prefix or None
    address: Optional[Address] = get_field(
        vcard, "adr", lambda f: is_type(f, "home")
    )
    org: Optional[Union[str, List[str]]] = get_field(vcard, "org")
    mail: Optional[str] = get_field(
        vcard, "email", lambda f: is_type(f, "home")
    )
    phone_home: Optional[str] = get_field(
        vcard, "tel", lambda f: is_type(f, ("voice", "home"))
    )
    phone_cell: Optional[str] = get_field(
        vcard, "tel", lambda f: is_type(f, ("voice", "cell"))
    )
    phone_work: Optional[str] = get_field(
        vcard, "tel", lambda f: is_type(f, ("voice", "work"))
    )

    return Contact(
        first_name,
        last_name,
        (None, None)
        if address is None
        else (address.street, " ".join((address.code, address.city))),
        mail,
        org if not isinstance(org, list) else " ".join(org),
        title,
        None
        if phone_home is None
        else FrozenPhoneNumber(parse(phone_home, env["DEFAULT_REGION"])),
        None
        if phone_cell is None
        else FrozenPhoneNumber(parse(phone_cell, env["DEFAULT_REGION"])),
        None
        if phone_work is None
        else FrozenPhoneNumber(parse(phone_work, env["DEFAULT_REGION"])),
        None,
    )
