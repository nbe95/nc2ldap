# Nextcloud to LDAP contact export

This is a simple Nextcloud plugin which servers all of a specific user's
contacts in an LDAP phone book.
It is meant to act as a simple backend for e.g. an OpenStage 40 SIP telephone.
The plugin runs an OpenLDAP server and imports all contacts' data on a
periodical basis.

## Prerequisites

### Hardware

In order to tell our OpenStage40 phone which data fields to have a look on, an
LDAP profile file must be transferred via FTP onto the phone once. Use the http
admin interface for that and refer to the manual for further information.

The easiest method is to setup a local Docker container (mind the :z-flags for
SELinux!):

```sh
docker run -d \
    --name ftp-server \
    -p 21:21 \
    -p 21000-21010:21000-21010 \
    -e USERS="foo|bar" \
    -v $(pwd):/home/ftp/:z \
    delfer/alpine-ftp-server
```

The LDAP profile can be downloaded via `Admin pages > File transfer > LDAP`.
To function properly, it must contain the following data attributes:

| Attribute         | Explanation                                           |
|-------------------|-------------------------------------------------------|
| SEARCHBASE        | The LDAP DN of the whole phonebook                    |
| ATTRIB01          | Last name                                             |
| ATTRIB02          | First name                                            |
| ATTRIB03          | Work phone number 1                                   |
| ATTRIB04          | Work phone number 2                                   |
| ATTRIB05          | Cell phone number                                     |
| ATTRIB06          | Home phone number                                     |
| ATTRIB07          | Organization/Business                                 |
| ATTRIB08          | Address 1 (street & house number)                     |
| ATTRIB09          | Address 2 (zip code & town)                           |
| ATTRIB10          | Title/name suffix                                     |
| ATTRIB11          | Mail address                                          |
| ATTRIB12 (opt.)   | Attribute to use for full wildcard search (e.g. "sn") |

Additionally, the LDAP server data and credentials must be configured once using
`Admin pages > System > Local functions > Directory settings`.

> Note: The default admin PIN for accessing the web interface is 123456.

### Software

In order to make this plugin work, you will want to create a Nextcloud app
token, which has no direct file access, instead of using your plain credentials.
;)
This ensures that we can grab contact data without damaging any of your
Nextcloud files. Visit `{NEXTCLOUD_URL}/settings/user/security` and scroll down
to create a new token with the name "nc2ldap". Save the user name and the
password in the corresponding fields within the .env file.

> If file-not-found related problems arise, try to **capitalize the user name**.

## Build and run

Always use a virtual environment instead of your system's Python interpreter.

```sh
python -m venv venv
source venv/bin/active
pip install --upgrade tox
```

When making changes, simply run `tox -e lint` to automatically validate and
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
