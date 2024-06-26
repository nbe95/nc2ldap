"""Module to manage the Nextcloud client side."""

import logging
from typing import Generator, Set

from vobject.base import Component, readOne
from webdav4.client import Client

from constants import LOG_LEVEL
from contact import Contact, contact_from_vcard

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)


class AddressBook:
    """A WebDAV client to read our Nextcloud address book."""

    def __init__(self, host: str, address_book: str, username: str, app_token: str):
        """Create a WebDAV client and connect to the Nextcloud instance."""
        self.client: Client = Client(host, auth=(username.lower(), app_token))
        self.webdav_path: str = (
            "/remote.php/dav/addressbooks/users/" f"{username}/{address_book.lower()}"
        )
        logger.info("Connected WebDAV client to Nextcloud instance %s.", host)

    def get_vcf_files(self) -> Generator[str, None, None]:
        """Fetch a list of  vfc files representing this address book."""
        return (file["href"] for file in self.client.ls(self.webdav_path))

    def get_contacts(self) -> Set[Contact]:
        """Fetch all Nextcloud contacts as vCards."""
        result: Set[Contact] = set()
        for file in self.get_vcf_files():
            logger.debug("Reading vcf contact file %s.", file)

            with self.client.open(file) as handle:
                contact: Component = readOne(handle)
                logger.debug("Reading Nextcloud contact %s.", contact.fn.value)
                result.add(contact_from_vcard(contact))

        logger.info("Read a total of %i Nextcloud contacts.", len(result))
        return result
