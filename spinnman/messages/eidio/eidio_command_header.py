

class EIDIOCommandHeader(object):

    def __init__(self, command):
        self._command = command

    def write_eidio_header(self, byte_writer):
        byte_writer.write_byte(0)  # the flag for no prefix
        byte_writer.write_byte(1)  # the flag for command message
        byte_writer.write_byte(self._command)