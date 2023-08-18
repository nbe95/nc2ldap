"""Main app for Nextcloud to LDAP contact exporter."""

import logging
from os import environ as env

# from simple_scheduler.event import event_scheduler
from time import sleep

import phonenumbers

from contact import Contact
from phonebook import Phonebook

NIKLAS = Contact(
    first_name="Niklas",
    last_name="Bettgen",
    address=("Ulrichstr. 3", "46519 Alpen"),
    email="niklas@bettgen.de",
    company="Bertrandt Development GmbH",
    title="Bitschubser 1. Klasse",
    phone_private=phonenumbers.parse("+4928029589333"),
    phone_mobile=phonenumbers.parse("+4915170080598"),
)

MARION = Contact(
    first_name="Marion",
    last_name="Sadowski",
    address=("Ulrichstr. 3", "46519 Alpen"),
    email="marion@bettgen.de",
    phone_private=phonenumbers.parse("+49280295893334"),
)


def main():
    """Run main entry point."""
    logging.info(
        "Setting up task scheduler to run at %s.", env["IMPORT_SCHEDULE"]
    )
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
    logging.info("Starting import from Nextcloud.")

    phonebook: Phonebook = Phonebook(env["LDAP_SERVER"], env["LDAP_PHONEBOOK"])
    phonebook.login(env["LDAP_ADMIN_USER"], env["LDAP_ADMIN_PASSWORD"])
    phonebook.create()

    phonebook.add_contact(NIKLAS)
    phonebook.add_contact(MARION)

    logging.debug(phonebook.get_contacts())


if __name__ == "__main__":
    main()
