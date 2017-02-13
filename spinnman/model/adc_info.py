"""
ADCInfo
"""

# spinnman imports
from spinnman import constants

# general imports
import struct


class ADCInfo(object):
    """
    container for the ADC data thats been retrieved from a fpga
    """

    def __init__(self, adc_data, offset):
        """
        :param adc_data: bytes from an SCP packet containing adc\
                    information
        :type adc_data: str
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    message does not contain valid adc information
        """
        data = struct.unpack_from(
            "<"   # Little-endian
            "8H"  # uint16_t adc[8]
            "4h"  # int16_t t_int[4]
            "4h"  # int16_t t_ext[4]
            "4h"  # int16_t fan[4]
            "I"   # uint32_t warning
            "I",  # uint32_t shutdown
            adc_data, offset)

        self._voltage_1_2c = data[1] * constants.BMP_V_SCALE_2_5
        self._voltage_1_2b = data[2] * constants.BMP_V_SCALE_2_5
        self._voltage_1_2a = data[3] * constants.BMP_V_SCALE_2_5
        self._voltage_1_8 = data[4] * constants.BMP_V_SCALE_2_5
        self._voltage_3_3 = data[6] * constants.BMP_V_SCALE_3_3
        self._voltage_supply = data[7] * constants.BMP_V_SCALE_12
        self._temp_top = float(data[8]) * constants.BMP_TEMP_SCALE
        self._temp_btm = float(data[9]) * constants.BMP_TEMP_SCALE
        if data[12] != constants.BMP_MISSING_TEMP:
            self._temp_ext_0 = (float(data[12]) * constants.BMP_TEMP_SCALE)
        else:
            self._temp_ext_0 = None
        if data[13] != constants.BMP_MISSING_TEMP:
            self._temp_ext_1 = (float(data[13]) * constants.BMP_TEMP_SCALE)
        else:
            self._temp_ext_1 = None
        if data[16] != constants.BMP_MISSING_FAN:
            self._fan_0 = float(data[16])
        else:
            self._fan_0 = None
        if data[17] != constants.BMP_MISSING_FAN:
            self._fan_1 = float(data[17])
        else:
            self._fan_1 = None

    @property
    def voltage_1_2c(self):
        """
        property for voltage 1 2c
        """
        return self._voltage_1_2c

    @property
    def voltage_1_2b(self):
        """
        property for voltage 1 2b
        """
        return self._voltage_1_2b

    @property
    def voltage_1_2a(self):
        """
        property for voltage 1 2a
        """
        return self._voltage_1_2a

    @property
    def voltage_1_8(self):
        """
        property for voltage 1 8
        """
        return self._voltage_1_8

    @property
    def voltage_3_3(self):
        """
        property for voltage 3 3
        """
        return self._voltage_3_3

    @property
    def voltage_supply(self):
        """
        property for voltage supply
        """
        return self._voltage_supply

    @property
    def temp_top(self):
        """
        property for temp_top
        """
        return self._temp_top

    @property
    def temp_btm(self):
        """
        property for temp btm
        """
        return self._temp_btm

    @property
    def temp_ext_0(self):
        """
        property for temp ext 0
        """
        return self._temp_ext_0

    @property
    def temp_ext_1(self):
        """
        property for temp_ext_1
        """
        return self._temp_ext_1

    @property
    def fan_0(self):
        """
        property for fan 0
        """
        return self._fan_0

    @property
    def fan_1(self):
        """
        property for fan 1
        """
        return self._fan_1
