ARG BASE_IMAGE_VERSION
FROM python:${BASE_IMAGE_VERSION}

ARG POETRY_VERSION

ENV PATH=/root/.local/bin:$PATH
RUN --mount=type=tmpfs,target=/root/.cargo --mount=type=bind,source=install.py,target=/install.py set -eux; \
    if grep -q alpine /etc/os-release && [ "$(arch)" = "aarch64" ]; then \
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
        POETRY_VERSION=$POETRY_VERSION python /install.py || cat /poetry-installer-error-*.log ; \
    fi ; \
    poetry --version

CMD ["python3"]
