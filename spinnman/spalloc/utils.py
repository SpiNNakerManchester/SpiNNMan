# Copyright (c) 2021 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from typing import Iterable, Tuple
from urllib.parse import urlparse, urlunparse


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
    :return: URL, username (may be None), password (may be None)
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


def is_server_address(
        address: str, additional_schemes: Iterable[str] = ()) -> bool:
    """
    Test if the given address is a likely spalloc server URL.

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
