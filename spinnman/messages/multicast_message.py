# Copyright (c) 2014 The University of Manchester
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

from typing import Optional


class MulticastMessage(object):
    """
    A SpiNNaker Multicast message, comprising a key (determining the target
    locations) and an optional payload.
    """
    __slots__ = (
        "_key",
        "_payload")

    def __init__(self, key: int, payload: Optional[int] = None):
        """
        :param key: The key of the packet
        :param payload: The optional payload of the packet
        """
        self._key = key
        self._payload = payload

    @property
    def key(self) -> int:
        """ The key of the packet. """
        return self._key

    @property
    def payload(self) -> Optional[int]:
        """
        The payload of the packet if there is one, or `None` if there is no
        payload.
        """
        return self._payload
