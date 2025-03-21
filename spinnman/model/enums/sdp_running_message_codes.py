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

from enum import Enum


# pylint: disable=invalid-name
class SDP_RUNNING_MESSAGE_CODES(Enum):
    """
    Codes for sending control messages to spin1_api.
    """
    SDP_STOP_ID_CODE = 6
    SDP_NEW_RUNTIME_ID_CODE = 7
    SDP_UPDATE_PROVENCE_REGION_AND_EXIT = 8
    SDP_CLEAR_IOBUF_CODE = 9
    SDP_PAUSE_ID_CODE = 10
    SDP_GET_CURRENT_TIME_CODE = 11
