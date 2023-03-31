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
from functools import wraps
from logging import getLogger
import re
import requests
from typing import Dict, Tuple
import websocket
from spinn_utilities.log import FormatAdapter
from .utils import clean_url
from spinnman.exceptions import SpallocException

logger = FormatAdapter(getLogger(__name__))
#: The name of the session cookie issued by Spring Security
_SESSION_COOKIE = "JSESSIONID"
#: Enable detailed debugging by setting to True
_debug_pretty_print = False


def _may_renew(method):
    def pp_req(req: requests.PreparedRequest):
        """
        :param ~requests.PreparedRequest req:
        """
        print('{}\n{}\r\n{}\r\n\r\n{}'.format(
            '>>>>>>>>>>>START>>>>>>>>>>>',
            req.method + ' ' + req.url,
            '\r\n'.join('{}: {}'.format(*kv) for kv in req.headers.items()),
            req.body if req.body else ""))

    def pp_resp(resp: requests.Response):
        """
        :param ~requests.Response resp:
        """
        print('{}\n{}\r\n{}\r\n\r\n{}'.format(
            '<<<<<<<<<<<START<<<<<<<<<<<',
            str(resp.status_code) + " " + resp.reason,
            '\r\n'.join('{}: {}'.format(*kv) for kv in resp.headers.items()),
            # Assume we only get textual responses
            str(resp.content, "UTF-8") if resp.content else ""))

    @wraps(method)
    def call(self, *args, **kwargs):
        renew_count = 0
        while True:
            r = method(self, *args, **kwargs)
            if _debug_pretty_print:
                pp_req(r.request)
                pp_resp(r)
            if _SESSION_COOKIE in r.cookies:
                # pylint: disable=protected-access
                self._session_id = r.cookies[_SESSION_COOKIE]
            if r.status_code != 401 or not renew_count:
                return r
            self.renew()
            renew_count += 1

    return call


class Session:
    """
    Manages session credentials for the Spalloc client.

    .. warning::
        This class does not present a stable API for public consumption.
    """
    __slots__ = (
        "__login_form_url", "__login_submit_url", "__srv_base", "_service_url",
        "__username", "__password", "__token",
        "_session_id", "__csrf", "__csrf_header")

    def __init__(
            self, service_url: str,
            username: str = None, password: str = None, token: str = None,
            session_credentials: Tuple[Dict[str, str], Dict[str, str]] = None):
        """
        :param str service_url: The reference to the service.
            *Should not* include a username or password in it.
        :param str username: The user name to use
        :param str password: The password to use
        :param str token: The bearer token to use
        """
        url = clean_url(service_url)
        self.__login_form_url = url + "system/login.html"
        self.__login_submit_url = url + "system/perform_login"
        self._service_url = url
        self.__srv_base = url + "srv/spalloc/"
        self.__username = username
        self.__password = password
        self.__token = token
        if session_credentials:
            cookies, headers = session_credentials
            if _SESSION_COOKIE in cookies:
                self._session_id = cookies[_SESSION_COOKIE]
            for key, value in headers.items():
                if key == "Authorization":
                    # TODO: extract this?
                    pass
                else:
                    # Urgh
                    self.__csrf_header = key
                    self.__csrf = value

    def __handle_error_or_return(self, response):
        code = response.status_code
        if code >= 200 and code < 400:
            return response
        result = response.content
        raise ValueError(f"Unexpected response from server {code}\n"
                         f"    {str(result)}")

    @_may_renew
    def get(self, url: str, timeout: int = 10, **kwargs) -> requests.Response:
        """
        Do an HTTP ``GET`` in the session.

        :param str url:
        :param int timeout:
        :rtype: ~requests.Response
        """
        params = kwargs if kwargs else None
        cookies = {_SESSION_COOKIE: self._session_id}
        r = requests.get(url, params=params, cookies=cookies,
                         allow_redirects=False, timeout=timeout)
        logger.debug("GET {} returned {}", url, r.status_code)
        return self.__handle_error_or_return(r)

    @_may_renew
    def post(self, url: str, jsonobj: dict, timeout: int = 10,
             **kwargs) -> requests.Response:
        """
        Do an HTTP ``POST`` in the session.

        :param str url:
        :param int timeout:
        :param dict jsonobj:
        :rtype: ~requests.Response
        """
        params = kwargs if kwargs else None
        cookies, headers = self._credentials
        r = requests.post(url, params=params, json=jsonobj,
                          cookies=cookies, headers=headers,
                          allow_redirects=False, timeout=timeout)
        logger.debug("POST {} returned {}", url, r.status_code)
        return self.__handle_error_or_return(r)

    @_may_renew
    def put(self, url: str, data: str, timeout: int = 10,
            **kwargs) -> requests.Response:
        """
        Do an HTTP ``PUT`` in the session. Puts plain text *OR* JSON!

        :param str url:
        :param str data:
        :param int timeout:
        :rtype: ~requests.Response
        """
        params = kwargs if kwargs else None
        cookies, headers = self._credentials
        if isinstance(data, str):
            headers["Content-Type"] = "text/plain; charset=UTF-8"
        r = requests.put(url, params=params, data=data,
                         cookies=cookies, headers=headers,
                         allow_redirects=False, timeout=timeout)
        logger.debug("PUT {} returned {}", url, r.status_code)
        return self.__handle_error_or_return(r)

    @_may_renew
    def delete(self, url: str, timeout: int = 10,
               **kwargs) -> requests.Response:
        """
        Do an HTTP ``DELETE`` in the session.

        :param str url:
        :rtype: ~requests.Response
        """
        params = kwargs if kwargs else None
        cookies, headers = self._credentials
        r = requests.delete(url, params=params, cookies=cookies,
                            headers=headers, allow_redirects=False,
                            timeout=timeout)
        logger.debug("DELETE {} returned {}", url, r.status_code)
        return self.__handle_error_or_return(r)

    def renew(self) -> dict:
        """
        Renews the session, logging the user into it so that state modification
        operations can be performed.

        :returns: Description of the root of the service, without CSRF data
        :rtype: dict
        :raises SpallocException:
            If the session cannot be renewed.
        """
        if self.__token:
            r = requests.get(
                self.__login_form_url,
                headers={"Authorization": f"Bearer {self.__token}"},
                allow_redirects=False, timeout=10)
            if not r.ok:
                raise SpallocException(f"Could not renew session: {r.content}")
            self._session_id = r.cookies[_SESSION_COOKIE]
        else:
            # Step one: a temporary session so we can log in
            csrf_matcher = re.compile(
                r"""<input type="hidden" name="_csrf" value="(.*)" />""")
            r = requests.get(self.__login_form_url, allow_redirects=False,
                             timeout=10)
            logger.debug("GET {} returned {}",
                         self.__login_form_url, r.status_code)
            m = csrf_matcher.search(r.text)
            if not m:
                raise SpallocException("could not establish temporary session")
            csrf = m.group(1)
            session = r.cookies[_SESSION_COOKIE]

            # Step two: actually do the log in
            form = {
                "_csrf": csrf,
                "username": self.__username,
                "password": self.__password,
                "submit": "submit"
            }
            # NB: returns redirect that sets a cookie
            r = requests.post(self.__login_submit_url,
                              cookies={_SESSION_COOKIE: session},
                              allow_redirects=False,
                              data=form, timeout=10)
            logger.debug("POST {} returned {}",
                         self.__login_submit_url, r.status_code)
            self._session_id = r.cookies[_SESSION_COOKIE]
            # We don't need to follow that redirect

        # Step three: get the basic service data and new CSRF token
        obj = self.get(self.__srv_base).json()
        self.__csrf_header = obj["csrf-header"]
        self.__csrf = obj["csrf-token"]
        del obj["csrf-header"]
        del obj["csrf-token"]
        return obj

    @property
    def _credentials(self) -> Tuple[Dict[str, str], Dict[str, str]]:
        """
        The credentials for requests. *Serializable.*
        """
        cookies = {_SESSION_COOKIE: self._session_id}
        headers = {self.__csrf_header: self.__csrf}
        if self.__token:
            # This would be better off done once per session only
            headers["Authorization"] = f"Bearer {self.__token}"
        return cookies, headers

    def websocket(
            self, url: str, header: dict = None, cookie: str = None,
            **kwargs) -> websocket.WebSocket:
        """
        Create a websocket that uses the session credentials to establish
        itself.

        :param str url: Actual location to open websocket at
        :param dict(str,str) header: Optional HTTP headers
        :param str cookie:
            Optional cookies (composed as semicolon-separated string)
        :param kwargs: Other options to :py:func:`~websocket.create_connection`
        :rtype: ~websocket.WebSocket
        """
        # Note: *NOT* a renewable action!
        if header is None:
            header = {}
        header[self.__csrf_header] = self.__csrf
        if cookie is not None:
            cookie += ";" + _SESSION_COOKIE + "=" + self._session_id
        else:
            cookie = _SESSION_COOKIE + "=" + self._session_id
        return websocket.create_connection(
            url, header=header, cookie=cookie, **kwargs)

    def _purge(self):
        """
        Clears out all credentials from this session, rendering the session
        completely inoperable henceforth.
        """
        self.__username = None
        self.__password = None
        self._session_id = None
        self.__csrf = None


class SessionAware:
    """
    Connects to the session.

    .. warning::
        This class does not present a stable API for public consumption.
    """
    __slots__ = ("__session", "_url")

    def __init__(self, session: Session, url: str):
        self.__session = session
        self._url = clean_url(url)

    @property
    def _session_credentials(self):
        """
        The current session credentials.
        Only supposed to be called by subclasses.

        :rtype: tuple(dict(str,str),dict(str,str))
        """
        # pylint: disable=protected-access
        return self.__session._credentials

    @property
    def _service_url(self):
        """
        The main service URL.

        :rtype: str
        """
        # pylint: disable=protected-access
        return self.__session._service_url

    def _get(self, url: str, **kwargs) -> requests.Response:
        return self.__session.get(url, **kwargs)

    def _post(self, url: str, jsonobj: dict, **kwargs) -> requests.Response:
        return self.__session.post(url, jsonobj, **kwargs)

    def _put(self, url: str, data: str, **kwargs) -> requests.Response:
        return self.__session.put(url, data, **kwargs)

    def _delete(self, url: str, **kwargs) -> requests.Response:
        return self.__session.delete(url, **kwargs)

    def _websocket(self, url: str, **kwargs) -> websocket.WebSocket:
        """
        Create a websocket that uses the session credentials to establish
        itself.

        :param str url: Actual location to open websocket at
        :rtype: ~websocket.WebSocket
        """
        return self.__session.websocket(url, **kwargs)
