# poetry-docker

![Update](https://github.com/weastur/poetry-docker/workflows/Update/badge.svg)
![Build and Push](https://github.com/weastur/poetry-docker/workflows/Build%20and%20Push/badge.svg)
[![Docker Pulls](https://img.shields.io/docker/pulls/weastur/poetry)](https://hub.docker.com/r/weastur/poetry/)
![GitHub](https://img.shields.io/github/license/weastur/poetry-docker)

**non-windows** [Official Python](https://hub.docker.com/_/python/)
docker images with the addition of the latest [Poetry](https://python-poetry.org)

## Usage

Image tags are generating from the next template:
`{poetry-version}-python-{official-python-image-tag}`,
where `{poetry-version}` is numeric version or `latest`.

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
is still `python3`, like in a Official Image.

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

Every single step of build process runs with Drone CI/CD.

## Contributing

You need an amd64 Linux host with Docker installed.
macOS and Windows + WSL would likely work,
but I haven't tested it.
You can start from `.github/workflows/docker-build.yml` to inspect the build process.
The main files are `Dockerfile` and `run.sh`.

Also, you can use [pre-commit](https://pre-commit.com) to run some checks
locally before commit.

```bash
pre-commit install
```

## Support

If you want to support the development or say thanks, become a GitHub Sponsor or

<a href="https://www.buymeacoffee.com/weastur" target="_blank">
<img src="https://cdn.buymeacoffee.com/buttons/default-orange.png"
    alt="Buy Me A Coffee"
    height="41"
    width="174">
</a>

## License

MIT, see [LICENSE](./LICENSE).
