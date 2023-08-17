#!/usr/bin/env python3

"""Main app for Nextcloud to LDAP contact exporter."""

from os import environ as env

from phonebook import Phonebook

# from simple_scheduler.event import event_scheduler


def main():
    """Main entry point."""
    print(f"Setting up task scheduler to run at: {env['SCHEDULE']}")
    # event_scheduler.add_job(
    #    job_name="Nextcloud contacts to LDAP export",
    #    target=do_import,
    #    when=[env["SCHEDULE"]]
    # )
    # event_scheduler.run()
    do_import()


def do_import():
    """Import and update all Nextcloud contacts to the local LDAP server."""

    print("Starting import from Nextcloud.")

    phonebook: Phonebook = Phonebook(env["LDAP_SERVER"], env["LDAP_PHONEBOOK"])
    phonebook.login(env["LDAP_USER"], env["LDAP_PASSWORD"])
    phonebook.create()
    print(phonebook.get_contacts())


if __name__ == "__main__":
    main()
