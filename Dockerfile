# Build stage

ARG PYTHON_VERSION=3.11
FROM python:$PYTHON_BASE-slim AS builder

# Set up pdm and install Python dependencies
ENV PDM_CHECK_UPDATE=false
RUN pip install -U pdm
COPY pyproject.toml pdm.lock README.md /app/
COPY src/ /app/src

WORKDIR /app
RUN pdm install --check --prod --no-editable


# Run stage

FROM python:${PYTHON_VERSION}-bullseye

RUN mkdir -p /app
WORKDIR /app

# Retrieve packages from build stage
COPY --from=builder /app/.venv/ /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Install further LDAP dependencies
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

# Copy custom entrypoint
COPY entrypoint.sh /

ARG VERSION
ENV VERSION ${VERSION}

ENTRYPOINT [ "/entrypoint.sh" ]
