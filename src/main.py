"""Main app for Nextcloud to LDAP contact exporter."""

import logging
from os import environ as env

# from simple_scheduler.event import event_scheduler
from time import sleep
from typing import Set

from contact import Contact
from ldap import PhoneBook
from nextcloud import AddressBook

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if "DEBUG" in env else logging.INFO)


def main():
    """Run main entry point."""
    # logger.info(
    #     "Setting up task scheduler to run at %s.", env["IMPORT_SCHEDULE"]
    # )
    # event_scheduler.add_job(
    #    job_name="Nextcloud contacts to LDAP export",
    #    target=do_import,
    #    when=[env["SCHEDULE"]]
    # )
    # event_scheduler.run()

    do_import()
    while True:
        sleep(1)


def do_import():
    """Import and update all Nextcloud contacts to the local LDAP server."""
    logger.info("Starting import of Nextcloud address book.")
    nc_address_book: AddressBook = AddressBook(
        env["NEXTCLOUD_HOST"],
        env["NEXTCLOUD_ADDRESS_BOOK"],
        env["NEXTCLOUD_USER"],
        env["NEXTCLOUD_APP_TOKEN"],
    )
    nc_contacts: Set[Contact] = set(nc_address_book.get_contacts())

    logger.info("Gathering data from local LDAP phone book.")
    ldap_phone_book: PhoneBook = PhoneBook(
        env["LDAP_HOST"], env["LDAP_PHONE_BOOK"]
    )
    ldap_phone_book.login(env["LDAP_ADMIN_USER"], env["LDAP_ADMIN_PASSWORD"])
    ldap_phone_book.create()
    ldap_contacts: Set[Contact] = set(ldap_phone_book.get_contacts())

    contacts_to_delete: Set[Contact] = ldap_contacts - nc_contacts
    contacts_to_add: Set[Contact] = nc_contacts - ldap_contacts

    logger.info("Found %i total upstream contacts.", len(nc_contacts))
    logger.info("Found %i total local contacts.", len(ldap_contacts))
    logger.info("%i contacts will be deleted.", len(contacts_to_delete))
    logger.info("%i contacts will be added.", len(contacts_to_add))


if __name__ == "__main__":
    main()
