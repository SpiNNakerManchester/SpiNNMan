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

from typing import Iterable, Tuple
from urllib.parse import urlparse, urlsplit, urlunparse


def clean_url(url: str) -> str:
    """
    Add a ``/`` to the end of the path part of a URL if there isn't one.

    :param str url:
    :rtype: str
    """
    r = urlparse(url)
    parts = list(r)
    # Add a / to the end of the path if it isn't there
    if not parts[2].endswith("/"):
        parts[2] += "/"
    return urlunparse(parts)


def parse_service_url(url: str) -> Tuple[str, str, str]:
    """
    Parses a combined service reference.

    :param str url:
    :return: URL, username (may be `None`), password (may be `None`)
    :rtype: tuple(str,str,str)
    """
    pieces = urlparse(url)
    user = pieces.username
    password = pieces.password
    netloc = pieces.hostname
    if pieces.port is not None:
        netloc += f":{pieces.port}"
    url = urlunparse((
        pieces.scheme, netloc, pieces.path, None, None, None))
    return url, user, password


def get_hostname(url: str) -> str:
    """
    Parses a URL and extracts the hostname part.
    """
    return urlsplit(url).hostname


def is_server_address(
        address: str, additional_schemes: Iterable[str] = ()) -> bool:
    """
    Test if the given address is a likely Spalloc server URL.

    :param str address: The address to check
    :param ~collections.abc.Iterable(str) additional_schemes:
        Any additional URL schemes that should be considered to be successes;
        typically ``{"spalloc"}`` when looser matching is required.
    :rtype: bool
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
