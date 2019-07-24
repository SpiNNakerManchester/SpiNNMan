# Copyright (c) 2017-2019 The University of Manchester
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

import time


class TokenBucket(object):
    """ An implementation of the token bucket algorithm. Usage::

        >>> bucket = TokenBucket(80, 0.5)
        >>> print(bucket.consume(10))
        True

    Not thread safe.
    """

    __slots__ = ['_capacity', '_tokens', '_fill_rate', '_timestamp']

    def __init__(self, tokens, fill_rate):
        """
        :param tokens: the total tokens in the bucket
        :param fill_rate:\
            the rate in tokens/second that the bucket will be refilled.
        """
        self._capacity = float(tokens)
        self._tokens = float(tokens)
        self._fill_rate = float(fill_rate)
        self._timestamp = time.time()

    def consume(self, tokens, block=True):
        """ Consume tokens from the bucket. Returns True if there were\
            sufficient tokens.

        If there are not enough tokens and block is True, sleeps until the\
        bucket is replenished enough to satisfy the deficiency.

        If there are not enough tokens and block is False, returns False.

        It is an error to consume more tokens than the bucket _capacity.
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
        if self._tokens < self._capacity:
            now = time.time()
            delta = self._fill_rate * (now - self._timestamp)
            self._tokens = min(self._capacity, self._tokens + delta)
            self._timestamp = now
        return self._tokens
