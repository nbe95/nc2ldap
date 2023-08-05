#!/usr/bin/env python3

from simple_scheduler.event import event_scheduler
import ldap

LDAP_SERVER: str = "ldap://openldap:389"
LDAP_USER: str = "cn=admin,dc=bettgen,dc=de"
LDAP_PASSWORD: str = "foobar123"
SCHEDULE: str = "*|**:**" # see https://pypi.org/project/simple-scheduler/

def main():
    print(f"Setting up task scheduler to run at: {SCHEDULE}")
    event_scheduler.add_job(
        job_name="Nextcloud contacts to LDAP export",
        target=export,
        when=SCHEDULE
    )
    event_scheduler.run()

def export():
    print("Starting LDAP export.")

    print(f"Connecting to server at {LDAP_SERVER}.")
    l = ldap.initialize(LDAP_SERVER)

    print(f"Authorizing as user {LDAP_USER}.")
    l.simple_bind_s(LDAP_USER, LDAP_PASSWORD)

    print(l.search_s('ou=Testing,dc=stroeder,dc=de',ldap.SCOPE_SUBTREE,'(cn=fred*)',['cn','mail']))

    # 1. Running for the first time? Create LDAP phonebook if not existing


if __name__ == "__main__":
    main()
