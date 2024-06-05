# poetry-docker

![Update](https://github.com/weastur/poetry-docker/workflows/Update/badge.svg)
[![Python 3.8](https://github.com/weastur/poetry-docker/actions/workflows/docker-build-38.yml/badge.svg)](https://github.com/weastur/poetry-docker/actions/workflows/docker-build-38.yml)
[![Python 3.9](https://github.com/weastur/poetry-docker/actions/workflows/docker-build-39.yml/badge.svg)](https://github.com/weastur/poetry-docker/actions/workflows/docker-build-39.yml)
[![Python 3.10](https://github.com/weastur/poetry-docker/actions/workflows/docker-build-310.yml/badge.svg)](https://github.com/weastur/poetry-docker/actions/workflows/docker-build-310.yml)
[![Python 3.11](https://github.com/weastur/poetry-docker/actions/workflows/docker-build-311.yml/badge.svg)](https://github.com/weastur/poetry-docker/actions/workflows/docker-build-311.yml)
[![Python 3.12](https://github.com/weastur/poetry-docker/actions/workflows/docker-build-312.yml/badge.svg)](https://github.com/weastur/poetry-docker/actions/workflows/docker-build-312.yml)
[![Docker Pulls](https://img.shields.io/docker/pulls/weastur/poetry)](https://hub.docker.com/r/weastur/poetry/)
![GitHub](https://img.shields.io/github/license/weastur/poetry-docker)

**non-windows** [Official Python](https://hub.docker.com/_/python/)
docker images with the addition of the latest [Poetry](https://python-poetry.org)

## Usage

Image tags are generated from the next template:
`{poetry-version}-python-{official-python-image-tag}`,
where `{poetry-version}` is a numeric version or `latest`.

For example:

```Dockerfile
FROM weastur/poetry:1.5.1-python-3.11.4-bookworm
FROM weastur/poetry:1.5.1-python-3.11-alpine
FROM weastur/poetry:latest-python-3.11
```

There is one special tag - `latest` - which is equivalent to
`latest-python-latest`, so it's just the latest Poetry version
based on `python:latest` image.

### Usage with `docker run`

The image can be run with `docker run` command. Notice that the `COMMAND` inside
is still `python3`, like in an Official Image.

## Internals

The image itself is built on top of an Official Python Image, with the
reference Poetry's
[installer](https://github.com/python-poetry/install.python-poetry.org),
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

Every single step of the build process runs with GitHub Actions.

## Contributing

You need Docker installed.
You can start from `.github/workflows/docker-build.yml` to inspect the build process.
The main files are `Dockerfile` and `update.py`.

Also, you can use [pre-commit](https://pre-commit.com) to run some checks
locally before committing.

```bash
pre-commit install
```

## License

MIT, see [LICENSE](./LICENSE).
