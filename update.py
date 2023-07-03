#!/usr/bin/env python3

import urllib.request
import re

PYTHON_LIBRARY_URL = 'https://raw.githubusercontent.com/docker-library/official-images/master/library/python'
PARSING_PATTERN = re.compile(r"^Tags\:(?P<tags>.*)(\nSharedTags\:(?P<shared_tags>.*))?\nArchitectures\:(?P<architectures>.*)", re.MULTILINE)

response = urllib.request.urlopen(PYTHON_LIBRARY_URL)
data = response.read().decode('utf-8')

for match in PARSING_PATTERN.finditer(data):
    print(match.groupdict()['tags'])
    print(match.groupdict()['shared_tags'] or '')
    print(match.groupdict()['architectures'])
    print(100*'=')
