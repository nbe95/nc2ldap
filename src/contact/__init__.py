"""Main module for contact management."""

from .converters import contact_from_ldap_dict, contact_to_ldap_dict
from .main import Contact

__ALL__ = (Contact, contact_from_ldap_dict, contact_to_ldap_dict)
