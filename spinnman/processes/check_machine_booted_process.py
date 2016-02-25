from spinnman import constants
from spinnman.messages.scp.scp_result import SCPResult
from spinnman.model.chip_info import ChipInfo
from spinnman.messages.scp.impl.scp_read_link_request import SCPReadLinkRequest
from spinnman.messages.scp.impl.scp_version_request import SCPVersionRequest
from spinnman.exceptions import SpinnmanTimeoutException
from spinnman.messages.scp.impl.scp_read_memory_request \
    import SCPReadMemoryRequest

from collections import deque

import logging
import time

logger = logging.getLogger(__file__)


class CheckMachineBootedProcess(object):

    def __init__(self, connection, ignore_chips):
        self._connection = connection
        self._ignore_chips = ignore_chips

    def _send(self, request):
        response = request.get_scp_response()
        retries = 3
        result = None
        while retries > 0 and (result is None or result != SCPResult.RC_OK):
            try:
                self._connection.send_scp_request(request)
                result, _, data, offset = \
                    self._connection.receive_scp_response()
                if result == SCPResult.RC_OK:
                    response.read_bytestring(data, offset)
                    return result, response
                retries -= 1
            except SpinnmanTimeoutException:
                retries -= 1
        return result, None

    def _read_version(self, x, y):
        result, version_response = self._send(SCPVersionRequest(x, y, 0))
        if version_response is not None:
            return result, version_response.version_info
        return result, None

    def _read_chip_data(self, read_request):
        result, read_response = self._send(read_request)
        if read_response is not None:
            return result, ChipInfo(read_response.data, read_response.offset)
        return result, None

    def _read_0_0_data(self):
        read_request = SCPReadMemoryRequest(
            x=0, y=0, base_address=constants.SYSTEM_VARIABLE_BASE_ADDRESS,
            size=constants.SYSTEM_VARIABLE_BYTES)
        return self._read_chip_data(read_request)

    def _read_chip_down_link(self, x, y, link):
        read_request = SCPReadLinkRequest(
            x=x, y=y, link=link,
            base_address=constants.SYSTEM_VARIABLE_BASE_ADDRESS,
            size=constants.SYSTEM_VARIABLE_BYTES)
        return self._read_chip_data(read_request)

    def check_machine_is_booted(self):

        # Check that chip 0, 0 is booted
        result, chip_0_0_data = self._read_0_0_data()
        if chip_0_0_data is None:
            logger.error("Could not read from 0, 0: {}", result)
            return None

        # Go through the chips, link by link
        chip_search = deque([chip_0_0_data])
        seen_chips = set()
        while (len(chip_search) > 0):
            chip = chip_search.pop()
            seen_chips.add((chip.x, chip.y))
            for link in chip.links_available:
                _, chip_data = self._read_chip_down_link(chip.x, chip.y, link)
                if (chip_data is not None and
                        (chip_data.x, chip_data.y) not in seen_chips):
                    chip_search.append(chip_data)

        # Try to get the version number from each found chip
        version_info = None
        for x, y in seen_chips:
            if (self._ignore_chips is None or
                    not self._ignore_chips.is_chip(x, y)):

                # Retry up to 3 times
                retries = 3
                result = None
                while retries > 0:
                    result, version_info = self._read_version(x, y)
                    if version_info is not None:
                        break

                    # Wait between retries
                    time.sleep(0.5)
                    retries -= 1

                # If no version could be read, the machine might be faulty
                if version_info is None:
                    logger.error(
                        "Could not get version from chip {}, {}: {}".format(
                            x, y))
                    return None

        return version_info
