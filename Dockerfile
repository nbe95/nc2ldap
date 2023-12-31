FROM python:3-bullseye

RUN mkdir -p /nc2ldap
WORKDIR /nc2ldap


RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        slapd \
        ldap-utils \
        psmisc \
        python-dev \
        libsasl2-dev \
        libldap2-dev \
        libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN python -m pip install -r ./requirements.txt

COPY src/ src/
COPY entrypoint.sh /

ARG VERSION
ENV VERSION ${VERSION}

ENTRYPOINT [ "/entrypoint.sh" ]
