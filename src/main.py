"""Main app for Nextcloud to LDAP contact exporter."""

import logging
from os import environ as env

# from simple_scheduler.event import event_scheduler
from time import sleep

from phonebook import Phonebook

logging.basicConfig(level=logging.DEBUG if "DEBUG" in env else logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Run main entry point."""
    logger.info(
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
    logger.info("Starting import from Nextcloud.")

    phonebook: Phonebook = Phonebook(env["LDAP_SERVER"], env["LDAP_PHONEBOOK"])
    phonebook.login(env["LDAP_ADMIN_USER"], env["LDAP_ADMIN_PASSWORD"])
    phonebook.create()

    # phonebook.add_contact(NIKLAS)
    # phonebook.add_contact(MARION)

    logger.warning(phonebook.get_contacts())


if __name__ == "__main__":
    main()
