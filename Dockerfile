FROM python:3.11-bullseye

RUN mkdir -p /app
WORKDIR /app

# Install required LDAP dependencies
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

# Set up pdm and install Python dependencies
ENV PDM_CHECK_UPDATE=false
RUN pip install -U pdm
COPY pyproject.toml pdm.lock README.md /app/
COPY src/ /app/src

RUN pdm install --check --prod --no-editable
ENV PATH="/app/.venv/bin:$PATH"

# Apply custom entrypoint
COPY entrypoint.sh /

ARG VERSION
ENV VERSION=${VERSION}

ENTRYPOINT [ "/entrypoint.sh" ]
