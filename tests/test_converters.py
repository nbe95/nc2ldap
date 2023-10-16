"""Test contact converter functions."""

from typing import Any, Dict

import pytest
from phonenumbers import FrozenPhoneNumber, parse
from vobject.base import Component, readOne

from contact import (
    Contact,
    contact_from_ldap_dict,
    contact_from_vcard,
    contact_to_ldap_dict,
)


@pytest.mark.parametrize(
    ("contact", "expected"),
    [
        (Contact(), {"sn": ""}),
        (Contact("Noah", "Bettgen"), {"givenName": "Noah", "sn": "Bettgen"}),
        (
            Contact(
                phone_private=FrozenPhoneNumber(parse("+49 5555 123")),
                phone_mobile=FrozenPhoneNumber(parse("+49 5555 234")),
                phone_business1=FrozenPhoneNumber(parse("+49 5555 345")),
                phone_business2=FrozenPhoneNumber(parse("+49 5555 456")),
            ),
            {
                "sn": "",
                "homePhone": "+49 5555 123",
                "mobile": "+49 5555 234",
                "telephoneNumber": "+49 5555 345",
                "facsimileTelephoneNumber": "+49 5555 456",
            },
        ),
        (
            Contact(company="Black Cat & Paws Inc.", title="Verwöhnter Kater"),
            {
                "sn": "",
                "o": "Black Cat & Paws Inc.",
                "title": "Verwöhnter Kater",
            },
        ),
        (
            Contact(address=("Ulrichstr. 3", "46519 Alpen")),
            {"sn": "", "street": "Ulrichstr. 3", "l": "46519 Alpen"},
        ),
        (
            Contact(first_name="Noah", email="katze@katzenhaus.cat"),
            {"sn": "", "givenName": "Noah", "mail": "katze@katzenhaus.cat"},
        ),
    ],
)
def test_contact_to_ldap(contact: Contact, expected: Dict[str, Any]) -> None:
    """Check function converting a contact object to an LDAP dict."""
    result: Dict[str, Any] = contact_to_ldap_dict(contact)
    assert expected == result


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        ({}, Contact(last_name="<???>")),
        ({"sn": ""}, Contact(last_name="<???>")),
        (
            {"givenName": ["Noah"], "sn": "Bettgen"},
            Contact("Noah", "Bettgen"),
        ),
        (
            {
                "homePhone": ["+49 5555 123"],
                "mobile": ["+49 5555 234"],
                "telephoneNumber": "+49 5555 345",
                "facsimileTelephoneNumber": "+49 5555 456",
            },
            Contact(
                last_name="<???>",
                phone_private=FrozenPhoneNumber(parse("+49 5555 123")),
                phone_mobile=FrozenPhoneNumber(parse("+49 5555 234")),
                phone_business1=FrozenPhoneNumber(parse("+49 5555 345")),
                phone_business2=FrozenPhoneNumber(parse("+49 5555 456")),
            ),
        ),
        (
            {"o": "Black Cat & Paws Inc.", "title": ["Verwöhnter Kater"]},
            Contact(
                last_name="<???>",
                company="Black Cat & Paws Inc.",
                title="Verwöhnter Kater",
            ),
        ),
        (
            {"street": "Ulrichstr. 3", "l": ["46519 Alpen"]},
            Contact(
                last_name="<???>", address=("Ulrichstr. 3", "46519 Alpen")
            ),
        ),
        (
            {"givenName": "Noah", "mail": ["katze@katzenhaus.cat"]},
            Contact(
                last_name="<???>",
                first_name="Noah",
                email="katze@katzenhaus.cat",
            ),
        ),
    ],
)
def test_ldap_to_contact(data: Dict[str, Any], expected: Contact) -> None:
    """Check function converting an LDAP dict to a contact object."""
    result: Contact = contact_from_ldap_dict(data)
    assert expected == result


@pytest.mark.parametrize(
    ("serialized", "expected"),
    [
        (
            """
BEGIN:VCARD
VERSION:3.0
N:Bettgen;Noah;;Verwöhnter Kater;
FN:Noah Bettgen
ORG:Black Cat & Paws Inc.;
EMAIL;type=INTERNET;type=HOME;type=pref:katze@katzenhaus.cat
TEL;type=CELL;type=VOICE;type=pref:+49 5555 234
TEL;type=WORK;type=VOICE:05555 345
TEL;type=HOME;type=VOICE:+49 5555 123
TEL;type=HOME;type=FAX:+49 5555 999
TEL:+49 5555 888
item1.ADR;type=HOME;type=pref:;;Ulrichstr. 3;Alpen;;46519;Deutschland
item1.X-ABADR:de
END:VCARD
""",
            Contact(
                "Noah",
                "Bettgen",
                ("Ulrichstr. 3", "46519 Alpen"),
                "katze@katzenhaus.cat",
                "Black Cat & Paws Inc.",
                "Verwöhnter Kater",
                FrozenPhoneNumber(parse("+49 5555 123")),
                FrozenPhoneNumber(parse("+49 5555 234")),
                FrozenPhoneNumber(parse("+49 5555 345")),
                None,
            ),
        ),
        (
            """
BEGIN:VCARD
VERSION:3.0
N:One, Two, Three;;;Dres.;
FN:Dres. One, Two, Three
END:VCARD
""",
            Contact(last_name="One, Two, Three", title="Dres."),
        ),
        (
            """
BEGIN:VCARD
VERSION:3.0
N:Bettgen;Noah;;;
FN:Noah Bettgen
TEL;type=VOICE:+49 5555 123
TEL;type=CELL;type=VOICE:+49 5555 234
TEL:+49 5555 345
TEL;type=FAX:+49 5555 999
END:VCARD
""",
            Contact(
                first_name="Noah",
                last_name="Bettgen",
                phone_private=FrozenPhoneNumber(parse("+49 5555 123")),
                phone_mobile=FrozenPhoneNumber(parse("+49 5555 234")),
            ),
        ),
    ],
    ids=("General", "Multiple last names", "Telephone number assignment"),
)
def test_vcard_to_contact(serialized: str, expected: Contact):
    """Check function converting a vCard data structure to a contact object."""
    vcard: Component = readOne(serialized)
    result: Contact = contact_from_vcard(vcard)
    assert expected == result
