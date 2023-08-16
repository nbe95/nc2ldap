FROM python:3-bullseye

RUN mkdir -p /nc2ldap
WORKDIR /nc2ldap

COPY src/ .

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install -r ./requirements.txt

COPY entrypoint.sh /
ENTRYPOINT [ "/entrypoint.sh" ]
