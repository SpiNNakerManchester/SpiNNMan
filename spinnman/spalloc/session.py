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
from json.decoder import JSONDecodeError
import re
from typing import Any, Callable, Dict, Tuple, cast, Optional
import websocket  # type: ignore

import requests

from spinn_utilities.log import FormatAdapter
from spinn_utilities.typing.json import JsonObject
from spinnman.exceptions import SpallocException

from .utils import clean_url

logger = FormatAdapter(getLogger(__name__))
#: The name of the session cookie issued by Spring Security
_SESSION_COOKIE = "JSESSIONID"
#: Enable detailed debugging by setting to True
_debug_pretty_print = False


def _may_renew(method: Callable) -> Callable:
    def pp_req(request: requests.PreparedRequest) -> None:
        """
        Prints the request to the console.

        :param request:
        """
        print(">>>>>>>>>>>START>>>>>>>>>>>\n")
        print(f"{request.method} {request.url}")
        print('\r\n'.join(f'{key}: {value}'
                          for key, value in request.headers.items()))
        if request.body:
            print(request.body)

    def pp_resp(response: requests.Response) -> None:
        """
        Prints the response to the console.

        :param response:
        """
        print("<<<<<<<<<<<START<<<<<<<<<<<")
        print(f"{response.status_code} {response.reason}")
        print('\r\n'.join(f'{key}: {value}'
                          for key, value in response.headers.items()))
        print(str(response.content, "UTF-8") if response.content else "")

    @wraps(method)
    def call(self: 'Session', *args: Any, **kwargs: Any) -> None:
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
        "__login_form_url", "__login_submit_url", "__srv_base",
        "__service_url", "__username", "__password", "__token",
        "_session_id", "__csrf", "__csrf_header")

    def __init__(
            self, service_url: str,
            username: Optional[str] = None, password: Optional[str] = None,
            token: Optional[str] = None,
            session_credentials: Optional[
                Tuple[Dict[str, str], Dict[str, str]]] = None):
        """
        :param service_url: The reference to the service.
            *Should not* include a username or password in it.
        :param username: The user name to use
        :param password: The password to use
        :param token: The bearer token to use
        """
        url = clean_url(service_url)
        self.__login_form_url = url + "system/login.html"
        self.__login_submit_url = url + "system/perform_login"
        self.__service_url = url
        self.__srv_base = url + "srv/spalloc/"
        self.__username = username
        self.__password = password
        self.__token = token
        if session_credentials:
            cookies, headers = session_credentials
            if _SESSION_COOKIE in cookies:
                self._session_id: Optional[str] = cookies[_SESSION_COOKIE]
            for key, value in headers.items():
                if key == "Authorization":
                    # TODO: extract this?
                    pass
                else:
                    self.__csrf_header = key
                    self.__csrf: Optional[str] = value

    def __handle_error_or_return(self, response: requests.Response
                                 ) -> Optional[requests.Response]:
        """
        :returns: The response verified that it is not an error
        """
        code = response.status_code
        if code >= 200 and code < 400:
            return response
        result = response.content
        raise ValueError(f"Unexpected response from server {code}\n"
                         f"    {str(result)}")

    @_may_renew
    def get(self, url: str, timeout: int = 10, **kwargs: Any
            ) -> Optional[requests.Response]:
        """
        Do an HTTP ``GET`` in the session.

        :param url:
        :param timeout:  Time to wait for the call to return
        :param kwargs: Optional extra parameters to send with the request
        :returns: The response verified that it is not an error
        :raise ValueError: If the server rejects a request
        """
        params = kwargs if kwargs else None
        assert self._session_id is not None
        cookies = {_SESSION_COOKIE: self._session_id}
        r = requests.get(url, params=params, cookies=cookies,
                         allow_redirects=False, timeout=timeout)
        logger.debug("GET {} returned {}", url, r.status_code)
        return self.__handle_error_or_return(r)

    @_may_renew
    def post(self, url: str, json_dict: dict, timeout: int = 10,
             **kwargs: Any) -> Optional[requests.Response]:
        """
        Do an HTTP ``POST`` in the session.

        :param url:
        :param json_dict:
        :param timeout:  Time to wait for the call to return
        :param kwargs: Optional extra parameters to send with the request
        :returns: The response verified that it is not an error
        :raise ValueError: If the server rejects a request
        """
        params = kwargs if kwargs else None
        cookies, headers = self.credentials
        r = requests.post(url, params=params, json=json_dict,
                          cookies=cookies, headers=headers,
                          allow_redirects=False, timeout=timeout)
        logger.debug("POST {} returned {}", url, r.status_code)
        return self.__handle_error_or_return(r)

    @_may_renew
    def post_raw(self, url: str, data: bytes, timeout: int = 10,
                 **kwargs: Any) -> Optional[requests.Response]:
        """
        Do an HTTP ``POST`` in the session. Posts raw data!

        :param url:
        :param data:
        :param timeout:  Time to wait for the call to return
        :param kwargs: Optional extra parameters to send with the request
        :returns: The response verified that it is not an error
        :raise ValueError: If the server rejects a request
        """
        params = kwargs if kwargs else None
        cookies, headers = self.credentials
        headers["Content-Type"] = "application/octet-stream"
        r = requests.post(url, params=params, data=data,
                          cookies=cookies, headers=headers,
                          allow_redirects=False, timeout=timeout)
        logger.debug("POST {} returned {}", url, r.status_code)
        return self.__handle_error_or_return(r)

    @_may_renew
    def put(self, url: str, data: str, timeout: int = 10,
            **kwargs: Any) -> Optional[requests.Response]:
        """
        Do an HTTP ``PUT`` in the session. Puts plain text *OR* JSON!

        :param url:
        :param data:
        :param timeout:  Time to wait for the call to return
        :param kwargs: Optional extra parameters to send with the request
        :returns: The response verified that it is not an error
        :raise ValueError: If the server rejects a request
        """
        params = kwargs if kwargs else None
        cookies, headers = self.credentials
        if isinstance(data, str):
            headers["Content-Type"] = "text/plain; charset=UTF-8"
        r = requests.put(url, params=params, data=data,
                         cookies=cookies, headers=headers,
                         allow_redirects=False, timeout=timeout)
        logger.debug("PUT {} returned {}", url, r.status_code)
        return self.__handle_error_or_return(r)

    @_may_renew
    def delete(self, url: str, timeout: int = 10,
               **kwargs: Any) -> Optional[requests.Response]:
        """
        Do an HTTP ``DELETE`` in the session.

        :param url:
        :param timeout:  Time to wait for the call to return
        :param kwargs: Optional extra parameters to send with the request
        :returns: The response verified that it is not an error
        :raise ValueError: If the server rejects a request

        """
        params = kwargs if kwargs else None
        cookies, headers = self.credentials
        r = requests.delete(url, params=params, cookies=cookies,
                            headers=headers, allow_redirects=False,
                            timeout=timeout)
        logger.debug("DELETE {} returned {}", url, r.status_code)
        return self.__handle_error_or_return(r)

    def renew(self) -> JsonObject:
        """
        Renews the session, logging the user into it so that state modification
        operations can be performed.

        :returns: Description of the root of the service, without CSRF data
        :raises SpallocException:
            If the session cannot be renewed.
        """
        if self.__token:
            r = requests.get(
                self.__login_form_url,
                headers={"Authorization": f"Bearer {self.__token}"},
                allow_redirects=False, timeout=10)
            if not r.ok:
                raise SpallocException(
                    f"Could not renew session: {cast(str, r.content)}")
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
                msg = ("Could not establish temporary session to "
                       f"{self.__service_url} for user {self.__username} ")
                if self.__password is None:
                    msg += "with a no password"
                else:
                    msg += f"with a {len(self.__password)} character password."
                raise SpallocException(msg)
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
            try:
                self._session_id = r.cookies[_SESSION_COOKIE]
            except KeyError as e:
                try:
                    json_error = r.json()
                    if 'message' in json_error:
                        error = json_error['message']
                    else:
                        error = str(json_error)
                except JSONDecodeError:
                    error = r.raw
                raise SpallocException(f"Unable to login: {error}") from e

        # Step three: get the basic service data and new CSRF token
        obj: JsonObject = self.get(self.__srv_base).json()
        self.__csrf_header = cast(str, obj["csrf-header"])
        self.__csrf = cast(str, obj["csrf-token"])
        del obj["csrf-header"]
        del obj["csrf-token"]
        return obj

    @property
    def credentials(self) -> Tuple[Dict[str, str], Dict[str, str]]:
        """
        The credentials for requests. *Serializable.*
        """
        assert self._session_id is not None
        assert self.__csrf is not None
        cookies = {_SESSION_COOKIE: self._session_id}
        headers = {self.__csrf_header: self.__csrf}
        if self.__token:
            # This would be better off done once per session only
            headers["Authorization"] = f"Bearer {self.__token}"
        return cookies, headers

    def websocket(
            self, url: str, header: Optional[dict] = None,
            cookie: Optional[str] = None,
            **kwargs: Any) -> websocket.WebSocket:
        """
        Create a websocket that uses the session credentials to establish
        itself.

        :param url: Actual location to open websocket at
        :param header: Optional HTTP headers
        :param cookie:
            Optional cookies (composed as semicolon-separated string)
        :param kwargs: Other options to :py:func:`~websocket.create_connection`
        :returns: Socket based on these credentials
        """
        # Note: *NOT* a renewable action!
        if header is None:
            header = {}
        header[self.__csrf_header] = self.__csrf
        assert self._session_id is not None
        if cookie is not None:
            cookie += ";" + _SESSION_COOKIE + "=" + self._session_id
        else:
            cookie = _SESSION_COOKIE + "=" + self._session_id
        return websocket.create_connection(
            url, header=header, cookie=cookie, **kwargs)

    def purge(self) -> None:
        """
        Clears out all credentials from this session, rendering the session
        completely inoperable henceforth.
        """
        self.__username = None
        self.__password = None
        self._session_id = None
        self.__csrf = None

    @property
    def service_url(self) -> str:
        """
        Get the service URL for this session.
        """
        return self.__service_url


class SessionAware:
    """
    Connects to the session.

    .. warning::
        This class does not present a stable API for public consumption.
    """
    __slots__ = ("__session", "_url")

    def __init__(self, session: Session, url: str):
        """
        :param session: The session created when starting the spalloc client
        :param url: job_url
        """
        self.__session = session
        self._url = clean_url(url)

    @property
    def _session_credentials(self) -> Tuple[Dict[str, str], Dict[str, str]]:
        """
        The current session credentials.
        Only supposed to be called by subclasses.
        """
        return self.__session.credentials

    @property
    def _service_url(self) -> str:
        """
        The main service URL.
        """
        return self.__session.service_url

    def _get(self, url: str, **kwargs: Any) -> requests.Response:
        return self.__session.get(url, **kwargs)

    def _post(self, url: str, json_dict: dict,
              **kwargs: Any) -> requests.Response:
        return self.__session.post(url, json_dict, **kwargs)

    def _post_raw(self, url: str, data: bytes,
                  **kwargs: Any) -> requests.Response:
        return self.__session.post_raw(url, data, **kwargs)

    def _put(self, url: str, data: str, **kwargs: Any) -> requests.Response:
        return self.__session.put(url, data, **kwargs)

    def _delete(self, url: str, **kwargs: Any) -> requests.Response:
        return self.__session.delete(url, **kwargs)

    def _websocket(self, url: str, **kwargs: Any) -> websocket.WebSocket:
        """
        Create a websocket that uses the session credentials to establish
        itself.

        :param url: Actual location to open websocket at
        """
        return self.__session.websocket(url, **kwargs)
