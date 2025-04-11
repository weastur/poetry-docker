#!/usr/bin/env python3

import json
import re
import typing
import urllib.request

from string import Template

IMAGE_NAME = "weastur/poetry"
POETRY_RELEASES_URL = (
    "https://api.github.com/repos/python-poetry/poetry/releases/latest"
)
PYTHON_IMAGE_METADATA_URL_TEMPLATE = "https://hub.docker.com/v2/namespaces/library/repositories/python/tags?page_size={page_size}&page={page}"
ALLOWED_VERSIONS = ["3.9", "3.10", "3.11", "3.12", "3.13"]
ALLOWED_ARCHITECTURES = {
    "amd64": [None, "v2", "v3", "v4"],
    "arm64": [None],
}
RESTRICTED_OS = [
    "alpine3.8",
    "alpine3.9",
    "alpine3.10",
    "alpine3.11",
    "alpine3.12",
    "alpine3.13",
    "alpine3.14",
    "alpine3.15",
    "alpine3.16",
    "alpine3.17",
    "alpine3.18",
    "alpine3.19",
    "stretch",
    "buster",
    "bullseye",
]
GH_ACTION_START = """---
name: Build and push

on:
  schedule:
    - cron: '0 0 * * 0'
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

      - name: Set up QEMU
        uses: docker/setup-qemu-action@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Download poetry installer
        run: |
          wget -q -S -O install.py https://install.python-poetry.org
"""

GH_ACTION_BUILD_AND_PUSH_STEP = Template(
    """
      - name: Build and push ($raw_tags)
        uses: docker/build-push-action@v6
        continue-on-error: false
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
        return "{}/{}/{}".format(
            image["os"], image["architecture"], image["variant"]
        )
    else:
        return "{}/{}".format(image["os"], image["architecture"])


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
            PYTHON_IMAGE_METADATA_URL_TEMPLATE.format(
                page_size=page_size, page=page
            )
        ) as response:
            data = json.loads(response.read().decode())
            metadata.extend(data["results"])
            if data["next"] is None:
                break
            page += 1
    return metadata


def _is_special(tag: str) -> bool:
    return tag == "latest" or tag.split("-")[0] == "3"


def _parse_version(tag: str) -> str:
    if _is_special(tag):
        return ALLOWED_VERSIONS[-1]
    for ver in ALLOWED_VERSIONS:
        if tag.startswith(ver):
            return ver


def _upd_max_version(tag: str, latest_version):
    if not re.fullmatch(r"^\d\.\d+\.\d+$", tag):
        return
    major_ver = _parse_version(tag)
    if not latest_version[major_ver] or int(tag.split(".")[2]) > int(
        latest_version[major_ver].split(".")[2]
    ):
        latest_version[major_ver] = tag


def _filter_images(images: list) -> list:
    pre_filtered = []
    latest_version = {ver: None for ver in ALLOWED_VERSIONS}
    for image in images:
        if (
            image.get("tag_status") != "active"
            or image.get("content_type") != "image"
        ):
            continue
        tag = image["name"]
        if not (
            _is_special(tag)
            or any(map(lambda ver: tag.startswith(ver), ALLOWED_VERSIONS))
        ):
            continue
        if "rc" in tag or any(
            map(lambda restricted_os: restricted_os in tag, RESTRICTED_OS)
        ):
            continue
        _upd_max_version(tag, latest_version)
        pre_filtered.append(image)
    filtered = []
    for image in pre_filtered:
        tag = image["name"]
        if not re.fullmatch(r"^\d\.\d+\.\d+.*", tag) or tag.startswith(
            latest_version[_parse_version(tag)]
        ):
            filtered.append(image)
    return filtered


poetry_version = _get_latest_poetry_version()
action = GH_ACTION_START

for metadata in _filter_images(_download_python_image_metadata()):
    tag = metadata["name"]
    platforms = []
    for image in metadata["images"]:
        if (
            image["os"] == "linux"
            and image["architecture"] in ALLOWED_ARCHITECTURES
            and image["variant"] in ALLOWED_ARCHITECTURES[image["architecture"]]
        ):
            platforms.append(_make_platform(image))
    if platforms:
        action += GH_ACTION_BUILD_AND_PUSH_STEP.substitute(
            raw_tags=tag,
            platforms=",".join(platforms),
            tags=_make_tags(tag, poetry_version),
            poetry_version=poetry_version,
            base_image_version=tag,
        )

with open(".github/workflows/docker-build.yml", "w") as file:
    file.write(action)
