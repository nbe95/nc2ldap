# Nextcloud to LDAP contact export

This is a simple Nextcloud plugin which servers all of a specific user's
contacts in an LDAP phone book.
It is meant to act as a simple backend for e.g. an OpenStage 40 SIP telephone.
The plugin runs an OpenLDAP server and imports all contacts' data on a
periodical basis.

## Build and run

```sh
docker build -t nc2ldap .
docker run -d --name nc2ldap \
    -p 389:389 \
    -p 636:636 \
    -e LDAP_ORGANIZATION=myorganisation \
    -e LDAP_DOMAIN=my.domain.tld \
    -e LDAP_ADMIN_PASSWORD=secret \
    nc2ldap
```

## LDAP debugging

```sh
docker run -d --name phpldapadmin \
    -p 6080:80 \
    -e PHPLDAPADMIN_LDAP_HOSTS=192.168.1.40 \
    -e PHPLDAPADMIN_HTTPS=false \
    osixia/phpldapadmin:0.9.0
```
