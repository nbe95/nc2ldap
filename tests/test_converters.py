"""Test contact converter functions."""

from typing import Any, Dict

import pytest
from phonenumbers import parse

from contact import Contact, contact_from_ldap_dict, contact_to_ldap_dict


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


# NIKLAS = Contact(
#     first_name="Niklas",
#     last_name="Bettgen",
#     address=("Ulrichstr. 3", "46519 Alpen"),
#     email="niklas@bettgen.de",
#     company="Bertrandt Development GmbH",
#     title="Bitschubser 1. Klasse",
#     phone_private=phonenumbers.parse("+4928029589333"),
#     phone_mobile=phonenumbers.parse("+4915170080598"),
# )
#
# MARION = Contact(
#     first_name="Marion",
#     last_name="Sadowski",
#     address=("Ulrichstr. 3", "46519 Alpen"),
#     email="marion@bettgen.de",
#     phone_private=phonenumbers.parse("+49280295893334"),
# )
#
