"""Main app for Nextcloud to LDAP contact exporter."""

import logging
from time import sleep
from typing import Set

from schedule import every, repeat, run_pending

from constants import (
    LDAP_ADMIN_PASSWORD,
    LDAP_ADMIN_USER,
    LDAP_HOST,
    LDAP_PHONE_BOOK,
    LOG_LEVEL,
    NEXTCLOUD_ADDRESS_BOOK,
    NEXTCLOUD_APP_TOKEN,
    NEXTCLOUD_HOST,
    NEXTCLOUD_SYNC_TIME,
    NEXTCLOUD_USER,
    VERSION,
)
from contact import Contact
from ldap import PhoneBook
from nextcloud import AddressBook

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)


def main():
    """Run main entry point."""
    logger.info("Starting nc2ldap v%s.", VERSION)
    logger.info("Setting up task scheduler to run every day at %s.", NEXTCLOUD_SYNC_TIME)

    # Perform an import once after start-up
    do_import()
    while True:
        run_pending()
        sleep(1)


@repeat(every().day.at(NEXTCLOUD_SYNC_TIME))
def do_import():
    """Import and update all Nextcloud contacts to the local LDAP server."""
    logger.info("Importing Nextcloud address book.")
    nc_address_book: AddressBook = AddressBook(
        NEXTCLOUD_HOST,
        NEXTCLOUD_ADDRESS_BOOK,
        NEXTCLOUD_USER,
        NEXTCLOUD_APP_TOKEN,
    )
    nc_contacts: Set[Contact] = nc_address_book.get_contacts()
    logger.info("Found %i upstream contacts.", len(nc_contacts))

    logger.info("Gathering data from local LDAP phone book.")
    ldap_phone_book: PhoneBook = PhoneBook(LDAP_HOST, LDAP_PHONE_BOOK)
    ldap_phone_book.login(LDAP_ADMIN_USER, LDAP_ADMIN_PASSWORD)
    ldap_phone_book.create()
    ldap_contacts: Set[Contact] = ldap_phone_book.get_contacts()
    logger.info("Found %i local contacts.", len(ldap_contacts))

    # Find out which contacts to add/delete by comparing them
    contacts_to_delete: Set[Contact] = ldap_contacts - nc_contacts
    contacts_to_add: Set[Contact] = nc_contacts - ldap_contacts

    logger.info("Deleting a total of %i contacts.", len(contacts_to_delete))
    for contact in contacts_to_delete:
        ldap_phone_book.delete_contact(contact)

    logger.info("Adding a total of %i contacts.", len(contacts_to_add))
    for contact in contacts_to_add:
        ldap_phone_book.add_contact(contact)


if __name__ == "__main__":
    main()
