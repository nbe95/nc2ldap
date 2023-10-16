"""Module contact conversion functions."""

import logging
from dataclasses import dataclass
from os import environ as env
from typing import Any, Dict, List, Optional, Tuple, Type, Union

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
logger.setLevel(logging.DEBUG if env.get("DEBUG", "") else logging.INFO)


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
    set_value(result, "sn", contact.last_name or " ")  # not optional
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
        wrapper_or_value: Optional[Union[List[str], str]] = attr.get(key)
        if wrapper_or_value is None:
            return None

        # Extract value if wrapped in a list
        value: str = wrapper_or_value
        if isinstance(wrapper_or_value, list):
            value = wrapper_or_value.pop()
            if wrapper_or_value:
                logger.error(
                    "LDAP key '%s' contains more than one value to extract.",
                    key,
                )
        value = value.strip()

        if value_type == FrozenPhoneNumber:
            try:
                return parse(value)
            except NumberParseException:
                return None
        return value

    return Contact(
        get_field(data, "givenName"),
        get_field(data, "sn") or None,
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
    # pylint: disable=too-many-locals

    @dataclass(frozen=True)
    class ValueAttrList:
        """Class for easy handling of values with specific attributes."""

        attr_list: List[str]
        value: Any

        def has_attr(self, type_str: str) -> bool:
            """Check whether this field has a specific attribute."""
            return type_str.lower() in (t.lower() for t in self.attr_list)

    def get_fields(vcard: Component, key: str) -> List[ValueAttrList]:
        """Get field list for a specific key with associated attributes."""
        return [
            ValueAttrList(
                [] if not item.params else item.type_paramlist,  # type: ignore
                item.value,  # type: ignore
            )
            for item in vcard.contents.get(key, [])
        ]

    def take_field_with_attr(
        fields: List[ValueAttrList], attr: str
    ) -> Tuple[Any, List[ValueAttrList]]:
        """Assign a specific value with attribute matching criteria."""
        filtered: List[ValueAttrList] = list(
            filter(lambda x: x.has_attr(attr), fields)
        )
        if not filtered:
            return (None, fields)

        target: Any = filtered.pop()
        if filtered:
            logger.warning(
                "Found multiple '%s' attributes in vCard for %s: %s",
                attr,
                vcard.fn.value,
                filtered,
            )
        fields.remove(target)
        return (target.value, fields)

    def take_first_field(
        fields: List[ValueAttrList],
    ) -> Tuple[Any, List[ValueAttrList]]:
        """Assign the first available attribute."""
        if not fields:
            return (None, fields)

        target = fields.pop()
        if fields:
            logger.warning(
                "Found multiple uncategorized attributes in vCard for %s: %s",
                vcard.fn.value,
                fields,
            )
        return (target.value, fields)

    # Match name and title (Note: The 'sn' attribute is not optional)
    first_name: Optional[str] = vcard.n.value.given or None
    last_name: str = (
        vcard.n.value.family
        if not isinstance(vcard.n.value.family, list)
        else ", ".join(str(n).strip() for n in vcard.n.value.family)
    )
    title: Optional[str] = vcard.n.value.prefix or None

    # Match address field(s)
    address: Optional[Address] = None
    all_addresses: List[ValueAttrList] = get_fields(vcard, "adr")
    if all_addresses:
        # If multiple values, take correct one; fall back to uncategorized
        address, all_addresses = take_field_with_attr(all_addresses, "home")
        if not address:
            address, all_addresses = take_first_field(all_addresses)

    # Match organization
    org: Optional[Union[str, List[str]]] = None
    all_orgs: List[ValueAttrList] = get_fields(vcard, "org")
    if all_orgs:
        org, all_orgs = take_first_field(all_orgs)

    # Match mail addresses
    mail: Optional[str] = None
    all_mails: List[ValueAttrList] = get_fields(vcard, "email")
    if all_mails:
        # If multiple values, take correct one; fall back to uncategorized
        mail, all_mails = take_field_with_attr(all_mails, "home")
        if not mail:
            mail, all_mails = take_first_field(all_mails)

    # Match phone numbers
    phone_home: Optional[str] = None
    phone_cell: Optional[str] = None
    phone_work: Optional[str] = None
    all_phones: List[ValueAttrList] = list(
        filter(lambda p: p.has_attr("voice"), get_fields(vcard, "tel"))
    )
    if all_phones:
        # If multiple phone numbers are present, try to find the right ones
        phone_home, all_phones = take_field_with_attr(all_phones, "home")
        phone_cell, all_phones = take_field_with_attr(all_phones, "cell")
        phone_work, all_phones = take_field_with_attr(all_phones, "work")

        # Fall back to any uncategorized phone numbers (home only)
        if not phone_home:
            phone_home, all_phones = take_first_field(all_phones)

    # Build an actual contact object using all information
    region: str = env.get("DEFAULT_REGION", "")
    print(region)
    return Contact(
        first_name=first_name,
        last_name=last_name,
        address=(
            (None, None)
            if address is None
            else (address.street, " ".join((address.code, address.city)))
        ),
        email=mail,
        company=org if not isinstance(org, list) else " ".join(org),
        title=title,
        phone_private=(
            None
            if phone_home is None
            else FrozenPhoneNumber(parse(phone_home, region))
        ),
        phone_mobile=(
            None
            if phone_cell is None
            else FrozenPhoneNumber(parse(phone_cell, region))
        ),
        phone_business1=(
            None
            if phone_work is None
            else FrozenPhoneNumber(parse(phone_work, region))
        ),
        phone_business2=None,
    )
