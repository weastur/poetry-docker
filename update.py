#!/usr/bin/env python3

import glob
import json
import os
import re
import urllib.request

from string import Template

IMAGE_NAME = "weastur/poetry"
POETRY_RELEASES_URL = (
    "https://api.github.com/repos/python-poetry/poetry/releases/latest"
)
PYTHON_IMAGE_METADATA_URL_TEMPLATE = "https://hub.docker.com/v2/namespaces/library/repositories/python/tags?page_size={page_size}&page={page}"
ALLOWED_VERSIONS = ["3.8", "3.9", "3.10", "3.11", "3.12"]
GH_ACTION_START = """---
name: Build and Push

on:
  schedule:
    - cron: '0 0 * * 1'
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
        username: $${{ secrets.DOCKERHUB_USERNAME }}
        password: $${{ secrets.DOCKERHUB_TOKEN }}

    - name: Download poetry installer
      run: |
        wget -q -S -O install.py https://install.python-poetry.org

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
"""

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


def _make_platform(image: dict) -> str:
    if image["variant"]:
        return "{}/{}/{}".format(image["architecture"], image["os"], image["variant"])
    else:
        return "{}/{}".format(image["architecture"], image["os"])


def _make_tags(raw_tags: str, poetry_version: str) -> str:
    tags = []
    for tag in raw_tags.split(", "):
        tags.append(f"{IMAGE_NAME}:latest-python-{tag}")
        tags.append(f"{IMAGE_NAME}:{poetry_version}-python-{tag}")
        if tag == "latest":
            tags.append(f"{IMAGE_NAME}:latest")
    return ",".join(tags)


def _download_python_image_metadata() -> list:
    page_size = 100
    page = 1
    metadata = []
    while True:
        with urllib.request.urlopen(
            PYTHON_IMAGE_METADATA_URL_TEMPLATE.format(page_size=page_size, page=page)
        ) as response:
            data = json.loads(response.read().decode())
            metadata.extend(data["results"])
            if data["next"] is None:
                break
            page += 1
    return metadata


poetry_version = _get_latest_poetry_version()
python_image_metadata = _download_python_image_metadata()
action = GH_ACTION_START

for metadata in python_image_metadata:
    if (
        metadata.get("tag_status") != "active"
        or metadata.get("content_type") != "image"
        or "windows" in metadata["name"]
    ):
        continue
    tag = metadata["name"]
    if (
        tag != "latest"
        and tag != "3"
        and not any(map(lambda ver: tag.startswith(ver), ALLOWED_VERSIONS))
    ):
        continue
    if not tag.split('-')[0].replace('.', '').isdigit() or 'rc' in tag:
        continue
    platforms = []
    for image in metadata["images"]:
        platforms.append(_make_platform(image))
    action += GH_ACTION_BUILD_AND_PUSH_STEP.substitute(
        raw_tags=tag,
        platforms=",".join(platforms),
        tags=_make_tags(tag, poetry_version),
        poetry_version=poetry_version,
        base_image_version=tag,
    )

with open(f".github/workflows/docker-build.yml", "w") as file:
    file.write(action)
