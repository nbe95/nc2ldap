# Nextcloud to LDAP contact export

This is a simple Nextcloud plugin which servers all of a specific user's
contacts in an LDAP phone book.
It is meant to act as a simple backend for e.g. an OpenStage 40 SIP telephone.
The plugin runs an OpenLDAP server and imports all contacts' data on a
periodical basis.

## Prerequisites

In order to tell our OpenStage40 phone which data fields to have a look on, an
LDAP profile file must be transferred via FTP onto the phone once. Use the http
admin interface for that and refer to the manual for further information.

The easiest method is to setup a local Docker container (mind the :z-flags for
SELinux!):

```sh
docker run -d \
    --name my-ftp-server \
    -e FTP_USER=foo \
    -e FTP_PASS=bar \
    -p 20-21:20-21/tcp \
    -p 40000-40009:40000-40009/tcp \
    -v/data:/home/user:z \
    garethflowers/ftp-server
```

## Build and run

Always use a virtual environment instead of your system's Python interpreter.

```sh
python -m venv venv
source venv/bin/active
```

When making changes, simply run `tox -e format` to automatically validate and
format the Python code. Executing `tox` will ensure functionality by running all
unit tests.

To build and run a Docker image, execute the following commands. Ensure you have
populated an `.env` file with proper values (see `.env.template`).

```sh
docker build -t nc2ldap .
docker run -d \
    --name nc2ldap \
    -p 389:389 \
    -p 636:636 \
    --env-file ./.env nc2ldap
```

## LDAP debugging

For debugging, simply attach a local running *phpldapadmin* container to the
target host.

```sh
TARGET=$(hostname -I)
docker run -d --name phpldapadmin \
    -p 6080:80 \
    -e PHPLDAPADMIN_LDAP_HOSTS=$TARGET \
    -e PHPLDAPADMIN_HTTPS=false \
    osixia/phpldapadmin:0.9.0
```
