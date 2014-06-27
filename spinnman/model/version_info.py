class VersionInfo(object):
    """ Decodes SC&MP/SARK version information as returned by the SVER command
    """

    def __init__(self, scp_message):
        """
        :param scp_message: SCPMessage containing the information
        :type scp_message: spinnman.scp.scp_message.SCPMessage
        :raise spinnman.exceptions.SCPInvalidParameterException: If the message\
                    does not contain valid version information
        """
        pass
        
    @property
    def version_information(self):
        """ The version information as text
        
        :return: The version information
        :rtype: str
        """
        pass
