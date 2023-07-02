ARG BASE_IMAGE_VERSION
FROM --platform=$BUILDPLATFORM python:${BASE_IMAGE_VERSION}

ARG POETRY_VERSION

ENV PATH=/root/.local/bin:$PATH
RUN --mount=type=bind,source=install.py,target=/install.py set -eux; \
    if grep -q alpine /etc/os-release ; then \
        apk add --no-cache --virtual .build-deps \
            gcc \
            linux-headers \
            libffi-dev \
            musl-dev \
            cargo \
        ; \
        POETRY_VERSION=$POETRY_VERSION python /install.py ; \
        apk del --no-network .build-deps; \
    else \
        apt-get update && apt-get install -y --no-install-recommends \
            build-essential \
            libssl-dev \
            libffi-dev \
            cargo \
            pkg-config \
        ; \
        POETRY_VERSION=$POETRY_VERSION python /install.py ; \
        apt-get purge -y \
            build-essential \
            libssl-dev \
            libffi-dev \
            cargo \
            pkg-config \
        ; \
        apt-get autoremove -y ; \
        rm -rf /var/lib/apt/lists/* ; \
    fi ; \
    poetry --version

CMD ["python3"]
