#!/bin/sh

set -ex

tags=$(wget -q -S -O - https://raw.githubusercontent.com/docker-library/official-images/master/library/python 2>&1 | grep -E '^(Tags|SharedTags)\:.*' | cut -d: -f2 | tr ', ' '\n' | grep -v windows | sort | uniq | tr '\n' ' ')
poetry_version=1.1.13
wget -q -S -O install.py https://install.python-poetry.org

if [ "$1" = "build" ]; then
    for tag in $tags; do
        DOCKER_BUILDKIT=1 docker build \
            --progress=plain \
            --pull \
            -f "Dockerfile" \
            --build-arg=BASE_IMAGE_VERSION="$tag" \
            --build-arg=POETRY_VERSION="$poetry_version" \
            --tag weastur/poetry:latest-python-"$tag" \
            --tag weastur/poetry:"$poetry_version"-python-"$tag" \
            "."
    done;
    docker tag weastur/poetry:latest-python-latest weastur/poetry:latest
elif [ "$1" = "push" ]; then
    docker push weastur/poetry:latest
    for tag in $tags; do
        docker push weastur/poetry:latest-python-"$tag"
        docker push weastur/poetry:"$poetry_version"-python-"$tag"
    done;
fi;
