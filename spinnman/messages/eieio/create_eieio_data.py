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

from spinnman.messages.eieio.data_messages import (
    EIEIODataMessage, EIEIODataHeader)


def read_eieio_data_message(data, offset):
    """
    Reads the content of an EIEIO data message and returns an object
    identifying the data which was contained in the packet.

    :param bytes data: data received from the network as a byte-string
    :param int offset: offset at which the parsing operation should start
    :return: an object which inherits from EIEIODataMessage which contains
        parsed data received from the network
    :rtype: EIEIODataMessage
    """
    eieio_header = EIEIODataHeader.from_bytestring(data, offset)
    offset += eieio_header.size
    return EIEIODataMessage(eieio_header, data, offset)
