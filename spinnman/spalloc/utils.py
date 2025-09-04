# Copyright (c) 2021 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Miscellaneous utilities for working with URLs relating to the Spalloc Client.
"""

from typing import Iterable, Tuple, Optional
from urllib.parse import urlparse, urlsplit, urlunparse


def clean_url(url: str) -> str:
    """
    Add a ``/`` to the end of the path part of a URL if there isn't one.

    :param url:
    :returns: url with `/` if needed.
    """
    r = urlparse(url)
    parts = list(r)
    # Add a / to the end of the path if it isn't there
    if not parts[2].endswith("/"):
        parts[2] += "/"
    return urlunparse(parts)


def parse_service_url(url: str) -> Tuple[str, Optional[str], Optional[str]]:
    """
    Parses a combined service reference. Must include a hostname.

    :param url:
    :return: URL, username (may be `None`), password (may be `None`)
    """
    pieces = urlparse(url)
    user = pieces.username
    password = pieces.password
    netloc = pieces.hostname
    if netloc is None:
        raise ValueError("URL must have a hostname")
    if pieces.port is not None:
        netloc += f":{pieces.port}"
    url = urlunparse((
        pieces.scheme, netloc, pieces.path, None, None, None))
    return url, user, password


def get_hostname(url: str) -> str:
    """
    Parses a URL and extracts the hostname part.
    A hostname must be present.

    :returns: the hostname part of the URL
    """
    netloc = urlsplit(url).hostname
    if netloc is None:
        raise ValueError("URL must have a hostname")
    return netloc


def is_server_address(
        address: str, additional_schemes: Iterable[str] = ()) -> bool:
    """
    Test if the given address is a likely Spalloc server URL.

    :param address: The address to check
    :param additional_schemes:
        Any additional URL schemes that should be considered to be successes;
        typically ``{"spalloc"}`` when looser matching is required.
    :returns: True if the address matches a pattern that could be a server..
    """
    schemes = {"http", "https"}
    if additional_schemes:
        schemes.update(additional_schemes)
    try:
        pieces = urlparse(address)
        scheme = pieces.scheme.lower()
        return scheme in schemes and pieces.netloc is not None
    except Exception:  # pylint: disable=broad-except
        return False
