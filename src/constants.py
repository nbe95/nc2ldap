"""Module for constants used in several source files."""

import logging
from os import environ

VERSION: str = environ.get("VERSION", "")
DEBUG: bool = bool(environ.get("DEBUG"))
LOG_LEVEL: int = logging.DEBUG if DEBUG else logging.INFO

NEXTCLOUD_SYNC_TIME: str = environ.get("SYNC_TIME", "00:00")
NEXTCLOUD_HOST: str = environ.get("NEXTCLOUD_HOST", "")
NEXTCLOUD_ADDRESS_BOOK: str = environ.get("NEXTCLOUD_ADDRESS_BOOK", "")
NEXTCLOUD_USER: str = environ.get("NEXTCLOUD_USER", "")
NEXTCLOUD_APP_TOKEN: str = environ.get("NEXTCLOUD_APP_TOKEN", "")

LDAP_HOST: str = environ.get("LDAP_HOST", "ldap://localhost:389")
LDAP_ADMIN_USER: str = environ.get("LDAP_ADMIN_USER", "cn=admin,dc=mytld,dc=com")
LDAP_ADMIN_PASSWORD: str = environ.get("LDAP_ADMIN_PASSWORD", "admin")
LDAP_PHONE_BOOK: str = environ.get("LDAP_PHONE_BOOK", "ou=phonebook,dc=mytld,dc=com")

DEFAULT_REGION: str = environ.get("DEFAULT_REGION", "")
