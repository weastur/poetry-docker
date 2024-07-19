ARG BASE_IMAGE_VERSION
FROM python:${BASE_IMAGE_VERSION}

ARG POETRY_VERSION

ENV PATH=/root/.local/bin:$PATH
RUN --mount=type=bind,source=install.py,target=/install.py set -eux; \
        POETRY_VERSION=$POETRY_VERSION python /install.py || cat /poetry-installer-error-*.log ; \
    poetry --version

CMD ["python3"]
