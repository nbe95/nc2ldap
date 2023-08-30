"""Test contact converter functions."""

from typing import Any, Dict

import pytest

from contact import Contact, contact_from_ldap_dict, contact_to_ldap_dict


@pytest.mark.parametrize(
    ("contact", "expected"),
    [
        (Contact(), {}),
    ],
    ids=["empty"],
)
def test_contact_to_ldap(contact: Contact, expected: Dict[str, Any]) -> None:
    """Check function converting a contact object to an LDAP dict."""
    assert contact_to_ldap_dict(contact) == expected


@pytest.mark.parametrize(
    "data,expected",
    [
        ({}, Contact()),
    ],
    ids=["empty"],
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
