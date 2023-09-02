"""Test contact converter functions."""

from typing import Any, Dict

import pytest
from phonenumbers import parse
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
        (Contact(), {}),
        (Contact("Noah", "Bettgen"), {"givenName": "Noah", "sn": "Bettgen"}),
        (
            Contact(
                phone_private=parse("+49 5555 123"),
                phone_mobile=parse("+49 5555 234"),
                phone_business1=parse("+49 5555 345"),
                phone_business2=parse("+49 5555 456"),
            ),
            {
                "homePhone": "+49 5555 123",
                "mobile": "+49 5555 234",
                "telephoneNumber": "+49 5555 345",
                "facsimileTelephoneNumber": "+49 5555 456",
            },
        ),
        (
            Contact(company="Black Cat & Paws Inc.", title="Verwöhnter Kater"),
            {"o": "Black Cat & Paws Inc.", "title": "Verwöhnter Kater"},
        ),
        (
            Contact(address=("Ulrichstr. 3", "46519 Alpen")),
            {"street": "Ulrichstr. 3", "l": "46519 Alpen"},
        ),
        (
            Contact(first_name="Noah", email="katze@katzenhaus.cat"),
            {"givenName": "Noah", "mail": "katze@katzenhaus.cat"},
        ),
    ],
)
def test_contact_to_ldap(contact: Contact, expected: Dict[str, Any]) -> None:
    """Check function converting a contact object to an LDAP dict."""
    assert contact_to_ldap_dict(contact) == expected


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        ({}, Contact()),
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
                phone_private=parse("+49 5555 123"),
                phone_mobile=parse("+49 5555 234"),
                phone_business1=parse("+49 5555 345"),
                phone_business2=parse("+49 5555 456"),
            ),
        ),
        (
            {"o": "Black Cat & Paws Inc.", "title": ["Verwöhnter Kater"]},
            Contact(company="Black Cat & Paws Inc.", title="Verwöhnter Kater"),
        ),
        (
            {"street": "Ulrichstr. 3", "l": ["46519 Alpen"]},
            Contact(address=("Ulrichstr. 3", "46519 Alpen")),
        ),
        (
            {"givenName": "Noah", "mail": ["katze@katzenhaus.cat"]},
            Contact(first_name="Noah", email="katze@katzenhaus.cat"),
        ),
    ],
)
def test_ldap_to_contact(data: Dict[str, Any], expected: Contact) -> None:
    """Check function converting an LDAP dict to a contact object."""
    assert contact_from_ldap_dict(data) == expected


def test_vcard_to_contact():
    """Check function converting a vCard data structure to a contact object."""

    serialized: str = """
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
"""
    expected: Contact = Contact(
        "Noah",
        "Bettgen",
        ("Ulrichstr. 3", "46519 Alpen"),
        "katze@katzenhaus.cat",
        "Black Cat & Paws Inc.",
        "Verwöhnter Kater",
        parse("+49 5555 123"),
        parse("+49 5555 234"),
        parse("+49 5555 345"),
        None,
    )

    vcard: Component = readOne(serialized)
    assert expected == contact_from_vcard(vcard)
