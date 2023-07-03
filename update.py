#!/usr/bin/env python3

import urllib.request
import re
import json

from string import Template

ARCH_TO_PLATFORM = {
    "amd64": "linux/amd64",
    "arm32v5": "linux/arm/v5",
    "arm32v6": "linux/arm/v6",
    "arm32v7": "linux/arm/v7",
    "arm64v8": "linux/arm64",
    "i386": "linux/386",
    "ppc64le": "linux/ppc64le",
    "s390x": "linux/s390x",
    "mips64le": "linux/mips64le",
}
IMAGE_NAME = "weastur/poetry"
POETRY_INSTALLER_URL = "https://install.python-poetry.org"
POETRY_RELEASES_URL = "https://api.github.com/repos/python-poetry/poetry/releases/latest"
PYTHON_LIBRARY_URL = "https://raw.githubusercontent.com/docker-library/official-images/master/library/python"
PARSING_PATTERN = re.compile(
    r"^Tags\:(?P<tags>(?!.*windows).*)(\nSharedTags\:(?P<shared_tags>.*))?\nArchitectures\:(?P<architectures>.*)",
    re.MULTILINE,
)
GH_ACTION_START = """---
name: Build and Push Docker Image

on:
  push:
    branches:
      - main

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
    - name: Check out code
      uses: actions/checkout@v3

    - name: Login to DockerHub
      uses: docker/login-action@v1
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v1
"""
GH_ACTION_BUILD_AND_PUSH_STEP = Template(
    """
    - name: Build and push ($raw_tags)
      uses: docker/build-push-action@v2
      with:
        context: .
        file: ./Dockerfile
        platforms: $platforms
        push: true
        tags: $tags
        build-args:
          BASE_IMAGE_VERSION: $base_image_version
          POETRY_VERSION: $poetry_version
"""
)


def _get_latest_poetry_version() -> str:
    with urllib.request.urlopen(POETRY_RELEASES_URL) as response:
        data = json.loads(response.read().decode())
        return data["tag_name"]


def _make_platforms(archs: str) -> str:
    return ",".join(ARCH_TO_PLATFORM[arch] for arch in archs.strip().split(", "))


def _make_tags(raw_tags: str, poetry_version: str) -> list[str]:
    tags = []
    for tag in raw_tags.split(", "):
        tags.append(f"{IMAGE_NAME}:latest-python-{tag}")
        tags.append(f"{IMAGE_NAME}:{poetry_version}-python-{tag}")
    return tags


with urllib.request.urlopen(PYTHON_LIBRARY_URL) as response:
    data = response.read().decode("utf-8")
urllib.request.urlretrieve(POETRY_INSTALLER_URL, "install.py")
action = GH_ACTION_START
poetry_version = _get_latest_poetry_version()

for match in PARSING_PATTERN.finditer(data):
    raw_tags = (
        match.groupdict()["tags"] + (match.groupdict()["shared_tags"] or "")
    ).strip()
    platforms = _make_platforms(match.groupdict()["architectures"])
    tags = _make_tags(raw_tags, poetry_version)
    action += GH_ACTION_BUILD_AND_PUSH_STEP.substitute(
        raw_tags=raw_tags,
        platforms=platforms,
        tags=tags,
        poetry_version=poetry_version,
        base_image_version=raw_tags.split(', ')[0],
    )

with open('.github/workflows/docker-build.yml', 'w') as file:
    file.write(action)
