# Nextcloud to LDAP contact export

This is a simple Nextcloud plugin which servers all of a specific user's
contacts in an LDAP phone book.
The plugin runs an OpenLDAP server and fetches all contact data periodically.

## Build and run

```sh
docker build -t nc2ldap .
docker run -d --name nextcloud-to-ldap nc2ldap \
    -p 389:389 \
    -p 636:636 \
    -e LDAP_ORGANISATION=myorganisation \
    -e LDAP_DOMAIN=my.domain.tld \
    -e LDAP_ADMIN_PASSWORD=secret
```
