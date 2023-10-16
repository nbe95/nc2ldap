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
        (Contact(first_name="Noah"), "Noah"),
        (Contact(last_name="Bettgen"), "Bettgen"),
        (Contact("Noah", "Bettgen"), "Noah Bettgen"),
        (
            Contact(title="Dr.", first_name="Noah", last_name="Bettgen"),
            "Dr. Noah Bettgen",
        ),
        (Contact(title="Dr.", last_name="Katzerich"), "Dr. Katzerich"),
        (Contact(company="Handbetrieb"), "(Handbetrieb)"),
        (
            Contact("Noah", "Bettgen", company="Schwarzkatz"),
            "Noah Bettgen (Schwarzkatz)",
        ),
        (Contact(email="katze@katzenhaus.cat"), "uuid"),
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
