"""Module to encapsulate the logic and functions of our LDAP phone book."""

import logging
from dataclasses import asdict
from os import environ as env
from typing import Any, Dict, Set

from ldap3 import ALL, ALL_ATTRIBUTES, Connection, Server

from contact import Contact, contact_from_ldap_dict, contact_to_ldap_dict

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if "DEBUG" in env else logging.INFO)


class PhoneBook:
    """Our LDAP phone book."""

    phone_book_ou: str = "organizationalUnit"
    contact_ou: str = "inetOrgPerson"

    def __init__(self, ldap_server: str, phone_book: str) -> None:
        """Create an LDAP server instance and connect to it."""
        self.phone_book: str = phone_book
        self.server: Server = Server(ldap_server, get_info=ALL)
        self.ldap: Connection
        logger.info("Connected to LDAP server %s.", ldap_server)

    def login(self, user: str, password: str) -> None:
        """Log in as a specific user in order to read and manipulate data."""
        self.ldap = Connection(
            self.server,
            user,
            password,
            client_strategy="SAFE_SYNC",
            auto_bind="NO_TLS",
        )
        logger.info("Authorized as user %s", user)

    def create(self) -> None:
        """Create our phone book as organizational unit if not existent yet."""
        # pylint: disable=unsubscriptable-object
        status, _result, response, _request = self.ldap.search(
            self.phone_book, f"(objectclass={self.phone_book_ou})"
        )
        if status:
            logger.info("Phone book %s is already present.", response[0]["dn"])
        else:
            self.ldap.add(self.phone_book, ["top", self.phone_book_ou])
            logger.info("Created new phone book %s.", self.phone_book)

    def get_contacts(self) -> Set[Contact]:
        """Read all contacts from the phone book."""
        _status, _result, response, _request = self.ldap.search(
            self.phone_book,
            f"(objectclass={self.contact_ou})",
            attributes=[ALL_ATTRIBUTES],
        )
        result: Set[Contact] = set()
        for item in response:
            attributes: Dict[str, Any] = item.get("attributes", {})
            try:
                contact: Contact = contact_from_ldap_dict(attributes)
                result.add(contact)
                logger.info("Successfully parsed LDAP contact %s.", contact)
            except TypeError:
                logger.error(
                    "Could not parse LDAP contact %s.", item.get("dn", "<?>")
                )
        return result

    def add_contact(self, contact: Contact) -> None:
        """Add a single contact to the phone book."""
        self.ldap.add(
            f"cn={contact.get_cn()},{self.phone_book}",
            [self.contact_ou],
            contact_to_ldap_dict(contact),
        )
        logger.info("Added %s to phone book.", contact)

    def delete_contact(self, contact: Contact) -> None:
        """Remove a single contact from the phone book."""
        self.ldap.delete(f"cn={contact.get_cn()},{self.phone_book}")
        logger.info("Deleted %s from phone book.", contact)
