FROM osixia/openldap:1.5.0

RUN mkdir -p /nc-ldap
COPY src/ /nc-ldap

RUN pip install -r /nc-ldap/requirements.txt

COPY entrypoint.sh /
ENTRYPOINT [ "/entrypoint.sh" ]
