"""Main module for contact management."""

from .contact import Contact
from .converters import (
    contact_from_ldap_dict,
    contact_from_vcard,
    contact_to_ldap_dict,
)

__ALL__ = (
    Contact,
    contact_from_ldap_dict,
    contact_to_ldap_dict,
    contact_from_vcard,
)
