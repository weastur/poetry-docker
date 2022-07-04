# poetry-docker

[![Build Status](https://drone.weastur.com/api/badges/weastur/poetry-docker/status.svg)](https://drone.weastur.com/weastur/poetry-docker)
[![Docker Pulls](https://img.shields.io/docker/pulls/weastur/poetry)](https://hub.docker.com/r/weastur/poetry/)
![GitHub](https://img.shields.io/github/license/weastur/poetry-docker)

Rebuilding of every actual **amd64 non-windows**
[Official Python](https://hub.docker.com/_/python/)
docker image with the addition of [Poetry](https://python-poetry.org)

## Usage

Image tags are generated from the next template:
`{poetry-version}-python-{official-python-image-tag}`,
where `{poetry-version}` is numeric version or `latest`.

For example:

```Dockerfile
FROM weastur/poetry:1.1.13-python-3.10.5-bullseye
FROM weastur/poetry:1.1.13-python-3.9-alpine
FROM weastur/poetry:latest-python-3.8
```

There is one special tag - `latest` - which is equivalent to
`latest-python-latest`, so it's just the latest Poetry version
based on `python:latest` image.

### Usage with `docker run`

The image can be run with `docker run` command. Notice that the `COMMAND` inside
is still `python3`, like in a Official Image.

## Internals

The image itself is built on top of an Official Python Image, with the
reference Poetry's
[installer](https://python-poetry.org/docs/master/#installing-with-the-official-installer),
which means that **there are no additional dependencies** in the
resulting image. For example:

```bash
➜ docker run -ti weastur/poetry bash
root@87ef07a9832a:/# pip list
Package    Version
---------- -------
pip        22.0.4
setuptools 58.1.0
wheel      0.37.1
```

Also, pay attention that **there are no additional settings** of Poetry,
like `poetry config virtualenvs.in-project true`
