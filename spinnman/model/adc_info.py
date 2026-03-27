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

import struct
from typing import Optional
from spinnman import constants

_PATTERN = struct.Struct(
    "<"   # Little-endian
    "8H"  # uint16_t adc[8]
    "4h"  # int16_t t_int[4]
    "4h"  # int16_t t_ext[4]
    "4h"  # int16_t fan[4]
    "I"   # uint32_t warning
    "I")  # uint32_t shutdown


class ADCInfo(object):
    """
    Container for the ADC data that's been retrieved from an FPGA.
    """
    __slots__ = [
        "_fan_0",
        "_fan_1",
        "_temp_btm",
        "_temp_ext_0",
        "_temp_ext_1",
        "_temp_top",
        "_voltage_1_2a",
        "_voltage_1_2b",
        "_voltage_1_2c",
        "_voltage_1_8",
        "_voltage_3_3",
        "_voltage_supply"]

    def __init__(self, adc_data: bytes, offset: int):
        """
        :param adc_data:
            bytes from an SCP packet containing ADC information
        :raise SpinnmanInvalidParameterException:
            If the message does not contain valid ADC information
        """
        data = _PATTERN.unpack_from(adc_data, offset)

        self._voltage_1_2c = data[1] * constants.BMP_V_SCALE_2_5
        self._voltage_1_2b = data[2] * constants.BMP_V_SCALE_2_5
        self._voltage_1_2a = data[3] * constants.BMP_V_SCALE_2_5
        self._voltage_1_8 = data[4] * constants.BMP_V_SCALE_2_5
        self._voltage_3_3 = data[6] * constants.BMP_V_SCALE_3_3
        self._voltage_supply = data[7] * constants.BMP_V_SCALE_12
        self._temp_top = float(data[8]) * constants.BMP_TEMP_SCALE
        self._temp_btm = float(data[9]) * constants.BMP_TEMP_SCALE
        if data[12] != constants.BMP_MISSING_TEMP:
            self._temp_ext_0: Optional[float] = (
                float(data[12]) * constants.BMP_TEMP_SCALE)
        else:
            self._temp_ext_0 = None
        if data[13] != constants.BMP_MISSING_TEMP:
            self._temp_ext_1: Optional[float] = (
                float(data[13]) * constants.BMP_TEMP_SCALE)
        else:
            self._temp_ext_1 = None
        if data[16] != constants.BMP_MISSING_FAN:
            self._fan_0: Optional[float] = float(data[16])
        else:
            self._fan_0 = None
        if data[17] != constants.BMP_MISSING_FAN:
            self._fan_1: Optional[float] = float(data[17])
        else:
            self._fan_1 = None

    @property
    def voltage_1_2c(self) -> float:
        """
        Actual voltage of the 1.2V c supply rail.
        """
        return self._voltage_1_2c

    @property
    def voltage_1_2b(self) -> float:
        """
        Actual voltage of the 1.2V b supply rail.
        """
        return self._voltage_1_2b

    @property
    def voltage_1_2a(self) -> float:
        """
        Actual voltage of the 1.2V a supply rail.
        """
        return self._voltage_1_2a

    @property
    def voltage_1_8(self) -> float:
        """
        Actual voltage of the 1.8V supply rail.
        """
        return self._voltage_1_8

    @property
    def voltage_3_3(self) -> float:
        """
        Actual voltage of the 3.3V supply rail.
        """
        return self._voltage_3_3

    @property
    def voltage_supply(self) -> float:
        """
        Actual voltage of the main power supply (nominally 12V).
        """
        return self._voltage_supply

    @property
    def temp_top(self) -> float:
        """
        Temperature top.
        """
        return self._temp_top

    @property
    def temp_btm(self) -> float:
        """
        Temperature bottom.
        """
        return self._temp_btm

    @property
    def temp_ext_0(self) -> Optional[float]:
        """
        Temperature external 0.
        """
        return self._temp_ext_0

    @property
    def temp_ext_1(self) -> Optional[float]:
        """
        Temperature external 1.
        """
        return self._temp_ext_1

    @property
    def fan_0(self) -> Optional[float]:
        """
        Fan 0.
        """
        return self._fan_0

    @property
    def fan_1(self) -> Optional[float]:
        """
        Fan 1.
        """
        return self._fan_1
