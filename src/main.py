"""Main app for Nextcloud to LDAP contact exporter."""

import logging
from os import environ as env
from time import sleep
from typing import Set

import schedule

from contact import Contact
from ldap import PhoneBook
from nextcloud import AddressBook

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if env.get("DEBUG", "") else logging.INFO)


def main():
    """Run main entry point."""
    logger.info(
        "Setting up task scheduler to run every day at %s.",
        env["IMPORT_TIME_UTC"],
    )

    # If running in debug mode, perform import once every minute
    if env.get("DEBUG", ""):
        schedule.every().minute().do(do_import)
    else:
        schedule.every().day.at(env["IMPORT_TIME_UTC"]).do(do_import)
    while True:
        schedule.run_pending()
        sleep(1)


def do_import():
    """Import and update all Nextcloud contacts to the local LDAP server."""
    logger.info("Importing Nextcloud address book.")
    nc_address_book: AddressBook = AddressBook(
        env["NEXTCLOUD_HOST"],
        env["NEXTCLOUD_ADDRESS_BOOK"],
        env["NEXTCLOUD_USER"],
        env["NEXTCLOUD_APP_TOKEN"],
    )
    nc_contacts: Set[Contact] = nc_address_book.get_contacts()
    logger.info("Found %i upstream contacts.", len(nc_contacts))

    logger.info("Gathering data from local LDAP phone book.")
    ldap_phone_book: PhoneBook = PhoneBook(
        env["LDAP_HOST"], env["LDAP_PHONE_BOOK"]
    )
    ldap_phone_book.login(env["LDAP_ADMIN_USER"], env["LDAP_ADMIN_PASSWORD"])
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
