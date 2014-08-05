from spinnman.messages.scp.abstract_messages.abstract_scp_request \
    import AbstractSCPRequest
from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.messages.sdp.sdp_flag import SDPFlag
from spinnman.messages.sdp.sdp_header import SDPHeader
from spinnman.messages.scp.scp_request_header import SCPRequestHeader
from spinnman.messages.scp.scp_command import SCPCommand
from spinnman.messages.scp.impl.scp_check_ok_response import SCPCheckOKResponse


class SCPApplicationRunRequest(AbstractSCPRequest):
    """ An SCP request to run an application loaded on a chip
    """

    def __init__(self, app_id, x, y, processors):
        """

        :param app_id: The id of the application to run, between 16 and 255
        :type app_id: int
        :param x: The x-coordinate of the chip to run on, between 0 and 255
        :type x: int
        :param y: The y-coordinate of the chip to run on, between 0 and 255
        :type y: int
        :param processors: The processors on the chip where the executable\
                    should be started, between 1 and 17
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If the app_id is out of range
                    * If the chip coordinates are out of range
                    * If one of the processors is out of range
        """
        if app_id < 16 or app_id > 255:
            raise SpinnmanInvalidParameterException(
                    "app_id", str(app_id), "Must be between 16 and 255")

        processor_mask = 0
        if processors is not None:
            for processor in processors:
                if processor < 1 or processor > 17:
                    raise SpinnmanInvalidParameterException(
                            "processors", str(processor),
                            "Each processor must be between 1 and 17")
                processor_mask |= (1 << processor)

        processor_mask |= (app_id << 24)

        super(SCPApplicationRunRequest, self).__init__(
                SDPHeader(
                    flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                    destination_cpu=0, destination_chip_x=x,
                    destination_chip_y=y),
                SCPRequestHeader(command=SCPCommand.CMD_AR),
                argument_1=processor_mask)

    def get_scp_response(self):
        """ See :py:meth:`spinnman.messages.scp.abstract_scp_request.AbstractSCPRequest.get_scp_response`
        """
        return SCPCheckOKResponse("Run Application", "CMD_AR")
