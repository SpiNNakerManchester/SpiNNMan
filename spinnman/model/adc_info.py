# spinnman imports
from spinnman import constants

# general imports
import struct

_PATTERN = struct.Struct(
    "<"   # Little-endian
    "8H"  # uint16_t adc[8]
    "4h"  # int16_t t_int[4]
    "4h"  # int16_t t_ext[4]
    "4h"  # int16_t fan[4]
    "I"   # uint32_t warning
    "I")  # uint32_t shutdown


class ADCInfo(object):
    """ Container for the ADC data thats been retrieved from a fpga
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

    def __init__(self, adc_data, offset):
        """
        :param adc_data: bytes from an SCP packet containing ADC information
        :type adc_data: str
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: \
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
        property for temp top
        """
        return self._temp_top

    @property
    def temp_btm(self):
        """
        property for temp bottom
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
        property for temp ext 1
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
