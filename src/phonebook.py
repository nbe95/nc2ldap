"""Module to encapsulate the logic and functions of our LDAP phonebook."""

import logging
from os import environ as env
from typing import Any, Dict, List

from ldap3 import ALL, ALL_ATTRIBUTES, Connection, Server

from contact import Contact, contact_from_ldap_dict, contact_to_ldap_dict

logging.basicConfig(level=logging.DEBUG if "DEBUG" in env else logging.INFO)
logger = logging.getLogger(__name__)


class Phonebook:
    """Our LDAP Phonebook."""

    phonebook_ou: str = "organizationalUnit"
    contact_ou: str = "inetOrgPerson"

    def __init__(self, ldap_server: str, phonebook: str) -> None:
        """Create an LDAP server instance and connect to it."""
        self.phonebook: str = phonebook
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
        """Create our phonebook as organizational unit if not existent yet."""
        # pylint: disable=unsubscriptable-object
        status, _result, response, _request = self.ldap.search(
            self.phonebook, f"(objectclass={self.phonebook_ou})"
        )
        if status:
            logger.info("Phonebook %s is already present.", response[0]["dn"])
        else:
            self.ldap.add(self.phonebook, ["top", self.phonebook_ou])
            logger.info("Created new phonebook %s.", self.phonebook)

    def get_contacts(self) -> List[Contact]:
        """Read all contacts from the phonebook."""
        _status, _result, response, _request = self.ldap.search(
            self.phonebook,
            f"(objectclass={self.contact_ou})",
            attributes=[ALL_ATTRIBUTES, "createTimestamp"],
        )
        result: List[Contact] = []
        for item in response:
            attributes: Dict[str, Any] = item.get("attributes", {})
            try:
                contact: Contact = contact_from_ldap_dict(attributes)
                result.append(contact)
                logger.info("Successfully parsed LDAP contact %s.", contact)
            except TypeError:
                logger.error(
                    "Could not parse LDAP contact %s.", item.get("dn", "<?>")
                )
        return result

    def add_contact(self, contact: Contact) -> bool:
        """Add a single contact to the phonebook."""
        self.ldap.add(
            f"cn={contact.get_cn()},{self.phonebook}",
            [self.contact_ou],
            contact_to_ldap_dict(contact),
        )
        logger.info("Added contact %s to phonebook.", contact)
        return False
