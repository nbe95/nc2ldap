"""Module to encapsulate the logic and functions of our LDAP phonebook."""

from typing import Any, Dict

from ldap3 import ALL, Connection, Server


class Phonebook:
    """Our LDAP Phonebook."""

    def __init__(self, ldap_server: str, phonebook: str) -> None:
        """Create an LDAP server instance and connect to it."""
        self.phonebook: str = phonebook
        self.phonebook_class: str = "organizationalUnit"
        self.server: Server = Server(ldap_server, get_info=ALL)
        self.ldap: Connection
        print(f"Connected to LDAP server {ldap_server}.")

    def login(self, user: str, password: str) -> None:
        """Log in as a specific user in order to read and manipulate data."""
        self.ldap = Connection(
            self.server,
            user,
            password,
            client_strategy="SAFE_SYNC",
            auto_bind="NO_TLS",
        )
        print(f"Authorized as user {user}.")

    def create(self) -> None:
        """Create our phonebook as organizational unit if not existent yet."""
        # pylint: disable=unsubscriptable-object
        status, _result, response, _request = self.ldap.search(
            self.phonebook, f"(objectclass={self.phonebook_class})"
        )
        if status:
            print(f"Phonebook {response[0]['dn']} is already present.")
        else:
            self.ldap.add(
                self.phonebook, object_class=["top", self.phonebook_class]
            )
            print(f"Created new phonebook {self.phonebook}.")

    def get_contacts(self) -> Dict[str, Any]:
        """Read all contacts from the phonebook."""
        return {}
