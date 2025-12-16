#!/bin/bash

start_server() {
    # (Re)start an LDAP server instance in background
    killall slapd
    slapd -h "ldap:/// ldapi:/// ldaps:///" -u openldap -g openldap -d "Stats,Stats2" &
    sleep 2
}

reconfigure_slapd() {
    # Customize slapd instance by running dpkg-reconfigure non-interactively
    echo "Reconfiguring slapd... this may take a minute."

    ORGANIZATION="${LDAP_ORGANIZATION:-MyOrganization}"
    DOMAIN="${LDAP_DOMAIN:-mytld.com}"
    ADMIN_PW="${LDAP_ADMIN_PASSWORD:-admin}"

    touch ./slapd.conf
    echo "slapd slapd/password1 password $ADMIN_PW" >> ./slapd.conf
    echo "slapd slapd/internal/adminpw password $ADMIN_PW" >> ./slapd.conf
    echo "slapd slapd/internal/generated_adminpw password $ADMIN_PW" >> ./slapd.conf
    echo "slapd slapd/password2 password $ADMIN_PW" >> ./slapd.conf
    echo "slapd slapd/unsafe_selfwrite_acl note" >> ./slapd.conf
    echo "slapd slapd/purge_database boolean false" >> ./slapd.conf
    echo "slapd slapd/domain string $DOMAIN" >> ./slapd.conf
    echo "slapd slapd/ppolicy_schema_needs_update select abort installation" >> ./slapd.conf
    echo "slapd slapd/invalid_config boolean true" >> ./slapd.conf
    echo "slapd slapd/move_old_database boolean true" >> ./slapd.conf
    echo "slapd slapd/backend select MDB" >> ./slapd.conf
    echo "slapd shared/organization string $ORGANIZATION" >> ./slapd.conf
    echo "slapd slapd/dump_database_destdir string /var/backups/slapd-VERSION" >> ./slapd.conf
    echo "slapd slapd/no_configuration boolean false" >> ./slapd.conf
    echo "slapd slapd/dump_database select when needed" >> ./slapd.conf
    echo "slapd slapd/password_mismatch note" >> ./slapd.conf

    debconf-set-selections ./slapd.conf
    dpkg-reconfigure -f noninteractive slapd
    rm ./slapd.conf
}


# Run slapd reconfiguration once at runtime (!)
init_file=/app/.slapd_init_done
if [ ! -e "$init_file" ]; then
    reconfigure_slapd
    touch "$init_file"
fi
start_server

# Start main script
echo "Starting nc2ldap application."
python -u -m nc2ldap.main
