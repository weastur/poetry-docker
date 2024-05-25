#!/usr/bin/env python3

import urllib.request
import re
import json

from string import Template

ARCH_TO_PLATFORM = {
    "riscv64": "linux/riscv64",
    "amd64": "linux/amd64",
    "arm32v5": "linux/arm/v5",
    "arm32v6": "linux/arm/v6",
    "arm32v7": "linux/arm/v7",
    "arm64v8": "linux/arm64",
    "i386": "linux/386",
    "mips64le": "linux/mips64le",
    "ppc64le": "linux/ppc64le",
    "s390x": "linux/s390x",
}
IMAGE_NAME = "weastur/poetry"
POETRY_RELEASES_URL = "https://api.github.com/repos/python-poetry/poetry/releases/latest"
PYTHON_LIBRARY_URL = "https://raw.githubusercontent.com/docker-library/official-images/master/library/python"
PARSING_PATTERN = re.compile(
    r"^Tags\:(?P<tags>(?!(.*windows|\ 3\.7.\d+|\ 3\.13.\d+)).*)(\nSharedTags\:(?P<shared_tags>.*))?\nArchitectures\:(?P<architectures>.*)",
    re.MULTILINE,
)
GH_ACTION_START = Template(
"""---
name: Build and Push ($_id)

on:
  schedule:
    - cron: '0 $hour * * 1'
  workflow_dispatch:

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
    - name: Check out code
      uses: actions/checkout@v4

    - name: Login to DockerHub
      uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}

    - name: Download poetry installer
      run: |
        wget -q -S -O install.py https://install.python-poetry.org

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
"""
)
GH_ACTION_BUILD_AND_PUSH_STEP = Template(
    """
    - name: Build and push ($raw_tags)
      uses: docker/build-push-action@v5
      with:
        context: .
        file: ./Dockerfile
        platforms: $platforms
        push: true
        tags: $tags
        build-args: |
          BASE_IMAGE_VERSION=$base_image_version
          POETRY_VERSION=$poetry_version
"""
)


def _get_latest_poetry_version() -> str:
    with urllib.request.urlopen(POETRY_RELEASES_URL) as response:
        data = json.loads(response.read().decode())
        return data["tag_name"]


def _make_platforms(archs: str) -> str:
    return ",".join(ARCH_TO_PLATFORM[arch] for arch in archs.strip().split(", "))


def _make_tags(raw_tags: str, poetry_version: str) -> str:
    tags = []
    for tag in raw_tags.split(", "):
        tags.append(f"{IMAGE_NAME}:latest-python-{tag}")
        tags.append(f"{IMAGE_NAME}:{poetry_version}-python-{tag}")
        if tag == 'latest':
            tags.append(f"{IMAGE_NAME}:latest")
    return ','.join(tags)


with urllib.request.urlopen(PYTHON_LIBRARY_URL) as response:
    data = response.read().decode("utf-8")
poetry_version = _get_latest_poetry_version()

for _id, match in enumerate(PARSING_PATTERN.finditer(data)):
    action = GH_ACTION_START.substitute(_id=_id, hour=_id % 24)
    raw_tags = match.groupdict()["tags"].strip()
    if match.groupdict()["shared_tags"]:
        raw_tags += ", " + match.groupdict()["shared_tags"].strip()
    raw_tags = raw_tags.strip()
    platforms = _make_platforms(match.groupdict()["architectures"])
    tags = _make_tags(raw_tags, poetry_version)
    action += GH_ACTION_BUILD_AND_PUSH_STEP.substitute(
        raw_tags=raw_tags,
        platforms=platforms,
        tags=tags,
        poetry_version=poetry_version,
        base_image_version=raw_tags.split(', ')[0],
    )
    with open(f'.github/workflows/docker-build-{_id}.yml', 'w') as file:
        file.write(action)
