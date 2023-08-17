# Nextcloud to LDAP contact export

This is a simple Nextcloud plugin which servers all of a specific user's
contacts in an LDAP phone book.
It is meant to act as a simple backend for e.g. an OpenStage 40 SIP telephone.
The plugin runs an OpenLDAP server and imports all contacts' data on a
periodical basis.

## Build and run

When making changes, simply run `tox` to automatically validate and format the
Python code.

```sh
docker build -t nc2ldap .
docker run -d --name nc2ldap -p 389:389 -p 636:636 --env-file ./.env nc2ldap
```

## LDAP debugging

```sh
docker run -d --name phpldapadmin \
    -p 6080:80 \
    -e PHPLDAPADMIN_LDAP_HOSTS=$(hostname -I) \
    -e PHPLDAPADMIN_HTTPS=false \
    osixia/phpldapadmin:0.9.0
```
