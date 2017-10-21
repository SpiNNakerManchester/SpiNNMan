from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.sdp import SDPFlag, SDPHeader
from spinnman.messages.scp import SCPRequestHeader
from .check_ok_response import CheckOKResponse

_WAIT_FLAG = 0x1 << 18


class ApplicationRun(AbstractSCPRequest):
    """ An SCP request to run an application loaded on a chip
    """

    def __init__(self, app_id, x, y, processors, wait=False):
        """

        :param app_id: The id of the application to run, between 16 and 255
        :type app_id: int
        :param x: The x-coordinate of the chip to run on, between 0 and 255
        :type x: int
        :param y: The y-coordinate of the chip to run on, between 0 and 255
        :type y: int
        :param processors: The processors on the chip where the executable\
                    should be started, between 1 and 17
        :type processors: list of int
        :param wait: True if the processors should enter a "wait" state on\
                    starting
        :type wait: bool
        """
        processor_mask = 0
        if processors is not None:
            for processor in processors:
                processor_mask |= (1 << processor)

        processor_mask |= (app_id << 24)
        if wait:
            processor_mask |= _WAIT_FLAG

        super(ApplicationRun, self).__init__(
            SDPHeader(flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                      destination_cpu=0, destination_chip_x=x,
                      destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_AR),
            argument_1=processor_mask)

    def get_scp_response(self):
        """ See\
            :py:meth:`spinnman.messages.scp.abstract_scp_request.AbstractSCPRequest.get_scp_response`
        """
        return CheckOKResponse("Run Application", "CMD_AR")
