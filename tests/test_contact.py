"""Test contact functions."""

from typing import Any, Dict
from uuid import UUID

import pytest
from phonenumbers import FrozenPhoneNumber, parse

from contact import Contact


def is_valid_uuid(uuid_to_test: str, version: int = 4):
    """Check if uuid_to_test is a valid UUID."""
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test


@pytest.mark.parametrize(
    ("contact", "expected"),
    [
        (Contact(), "uuid"),
        (Contact(first_name="Joey"), "Joey"),
        (Contact(last_name="Doe"), "Doe"),
        (Contact("Joey", "Doe"), "Joey Doe"),
        (
            Contact(title="Dr.", first_name="Joey", last_name="Doe"),
            "Dr. Joey Doe",
        ),
        (Contact(title="Dr.", last_name="Catto"), "Dr. Catto"),
        (Contact(company="Business"), "(Business)"),
        (
            Contact("Joey", "Doe", company="Black Cat"),
            "Joey Doe (Black Cat)",
        ),
        (Contact(email="cat@cathouse.cat"), "uuid"),
        (
            Contact(phone_private=FrozenPhoneNumber(parse("+49 5555 123"))),
            "uuid",
        ),
    ],
)
def test_get_cn(contact: Contact, expected: Dict[str, Any]) -> None:
    """Check function retreiving a CN from a contact object."""
    result: str = contact.get_cn()
    if expected == "uuid":
        assert is_valid_uuid(result)
    else:
        assert expected == result
