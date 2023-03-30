# Copyright (c) 2015 The University of Manchester
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

import time


class TokenBucket(object):
    """
    An implementation of the token bucket algorithm. Usage::

        >>> bucket = TokenBucket(80, 0.5)
        >>> print(bucket.consume(10))
        True

    Not thread safe.
    """

    __slots__ = ['_capacity', '_tokens', '_fill_rate', '_timestamp']

    def __init__(self, tokens, fill_rate):
        """
        :param int tokens: the total tokens in the bucket
        :param float fill_rate:
            the rate in tokens/second that the bucket will be refilled.
        """
        self._capacity = float(tokens)
        self._tokens = float(tokens)
        self._fill_rate = float(fill_rate)
        self._timestamp = time.time()

    def consume(self, tokens, block=True):
        """
        Consume tokens from the bucket. Returns True if there were
        sufficient tokens.

        If there are not enough tokens and block is True, sleeps until the
        bucket is replenished enough to satisfy the deficiency.

        If there are not enough tokens and block is False, returns False.

        It is an error to consume more tokens than the bucket capacity.

        :param int tokens:
        :param bool block:
        :rtype: bool
        """
        while block and tokens > self.tokens:
            deficit = tokens - self._tokens
            delay = deficit / self._fill_rate
            time.sleep(delay)

        if tokens <= self.tokens:
            self._tokens -= tokens
            return True
        return False

    @property
    def tokens(self):
        """
        The number of tokens currently in the bucket.

        :rtype: int
        """
        if self._tokens < self._capacity:
            now = time.time()
            delta = self._fill_rate * (now - self._timestamp)
            self._tokens = min(self._capacity, self._tokens + delta)
            self._timestamp = now
        return self._tokens
