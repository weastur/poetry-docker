ARG VERSION
FROM python:${VERSION}

ENV PATH=/root/.local/bin:$PATH
RUN --mount=type=bind,source=install.py,target=/install.py set -eux; \
    if grep -q alpine /etc/os-release ; then \
        apk add --no-cache --virtual .build-deps \
            gcc \
            linux-headers \
            libffi-dev \
            musl-dev \
        ; \
        python /install.py ; \
        apk del --no-network .build-deps; \
    else \
        python /install.py ; \
    fi ; \
    poetry --version

CMD ["python3"]
