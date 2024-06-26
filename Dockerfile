ARG BASE_IMAGE_VERSION
FROM python:${BASE_IMAGE_VERSION}

ARG POETRY_VERSION

ENV PATH=/root/.local/bin:$PATH
RUN --mount=type=tmpfs,target=/root/.cargo --mount=type=bind,source=install.py,target=/install.py set -eux; \
    if grep -q alpine /etc/os-release ; then \
        apk add --no-cache --virtual .build-deps \
            cargo \
            g++ \
            gcc \
            libffi-dev \
            linux-headers \
            musl-dev \
            openssl \
            openssl-dev \
        ; \
        POETRY_VERSION=$POETRY_VERSION python /install.py || cat /poetry-installer-error-*.log ; \
        apk del --no-network .build-deps; \
    else \
        apt-get update && apt-get install -y --no-install-recommends \
            build-essential \
            cargo \
            g++ \
            gcc \
            libffi-dev \
            libssl-dev \
            pkg-config \
        ; \
        POETRY_VERSION=$POETRY_VERSION python /install.py || cat /poetry-installer-error-*.log ; \
        apt-get purge -y \
            build-essential \
            cargo \
            g++ \
            gcc \
            libffi-dev \
            libssl-dev \
            pkg-config \
        ; \
        apt-get autoremove -y ; \
        rm -rf /var/lib/apt/lists/* ; \
    fi ; \
    poetry --version

CMD ["python3"]
