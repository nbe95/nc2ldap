# Nextcloud contacts to LDAP

This is a simple Nextcloud add-on serving all of a specific user's contacts as an LDAP phone book.
It is meant to run in a **standalone Docker container** and act as a simple backend for desk SIP
phones with LDAP support which, in my case, is an old and inexpensive *OpenStage 40* SIP telephone.

![Functional overview](./doc/overview.svg)

The plugin runs its own OpenLDAP server and imports all contacts' data on a periodical basis. With
the plugin running in the background and syncing contacts once per day from a single source of truth
(i.e. your Nextcloud instance), your desk phone can connect to its LDAP endpoint via network. It
then will be able to always provide the most recent names and phone numbers of your contacts and
dial them directly. Also, it may look up any incoming call and present the caller name on the
display, if they're known.

## Quick start

The server needs a bunch of config values to function properly, which can and should be stored in an
`.env` file. See and adapt the [.env file template](./.env.template) to fit your needs. Also, check
out the [software prerequisites](#software) below.

Then, you're ready to go:

```sh
docker run -d \
  --name nc2ldap \
  --env-file ./.env \
  --restart unless-stopped \
  -p 389:389 \
  nbe95/nc2ldap
```

If the container dies instantly, check its logs and make sure that your environment file contains
correct and plausible values, especially for the Nextcloud upstream credentials.

**Important:** The plugin is designed to run *in your local network*. A simple password is required
*to access any data on the LDAP server. However, there's no effort put into extra layers of data
*security, authentication, TLS etc. Do not publish any part of this service to the outside world.

> :information_source: If you're using a **Fritzbox as SIP server** and your phone is not smart
enough (like mine) to actively look up an incoming caller, you may consider synchronizing your
Nextcloud contacts to a dedicated Fritzbox phone book as well. Then, the Fritzbox itself will
recognize any known caller number and support the name of the caller directly to the phone via SIP
protocol - genius!

## Prerequisites

### Software

In order to make this plugin work, you will want to create a Nextcloud app token, which has no
direct file access, instead of using your plain credentials. :innocent:

This ensures that we can grab contact data without damaging any of your Nextcloud files. Visit
`{NEXTCLOUD_URL}/settings/user/security` and scroll down to create a new token with the name
"nc2ldap". Save the user name and the password in the corresponding fields within the `.env` file.

> :bulb: If file-not-found related problems arise, try to **capitalize the user name**.

### Hardware

> :warning: This section describes my very own setup using an *OpenStage 40* desk phone. Use for
inspiration purposes and, as usual, at your own risk. :wink:

In order to tell our desk phone which data fields to have a look on, an [LDAP profile
file](./doc/os40-ldap-profile.txt) must be transferred via FTP onto the phone once. Use the http
admin interface for that and refer to the manual for further information.

The easiest method is to setup a local Docker container (mind the `:z` flag for SELinux), for
example:

```sh
docker run -d \
  --name ftp-server \
  -p 21:21 \
  -p 21000-21010:21000-21010 \
  -e USERS="foo|bar" \
  -v $(pwd):/home/ftp/:z \
  delfer/alpine-ftp-server
```

The LDAP profile can be downloaded via `Admin pages > File transfer > LDAP`.  To function properly,
it must contain the following data attributes:

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
`Admin pages > Local functions > Directory settings`.

> Note: The default admin PIN for accessing the web interface is `123456`.

## Build and run

Install [pdm](https://pdm-project.org/). It handles virtual environments and package management for
you.

### Linting and formatting

When making changes, run `pdm run lint` to automatically lint and validate and the Python code.
Running `pdm run format` performs an auto-format and executing `pdm run test` will ensure
functionality by running all unit tests.

> :bulb: If you're not successful installing `python-ldap` and get wild errors like `command gcc
failed`, check out [this
article](https://www.python-ldap.org/en/python-ldap-3.3.0/installing.html#installing-from-source)
about installing the package from source.

### Building a Docker image

With each new release, the latest image will be automatically published to [Docker
Hub](https://hub.docker.com/r/nbe95/nc2ldap).

To build and run an image locally, execute `docker build -t nbe95/nc2ldap .` in the root directory.
Ensure you have populated an `.env` file with proper values (see `.env.template`).

### LDAP debugging

For debugging, I recommend the great tool
[phpLDAPadmin](https://github.com/osixia/docker-phpLDAPadmin), which also comes in a Docker
container. Simply attach a local running instance to the target host and have fun!

```sh
docker run -d --name phpldapadmin \
  -p 6080:80 \
  -e PHPLDAPADMIN_LDAP_HOSTS=$(hostname -I) \
  -e PHPLDAPADMIN_HTTPS=false \
  osixia/phpldapadmin:0.9.0
```
