from threading import Condition
from spinnman.model.io_buffer import IOBuffer
from spinnman.data.little_endian_byte_array_byte_reader \
    import LittleEndianByteArrayByteReader
from _scp_message_interface import SCPMessageInterface
from spinnman.messages.scp.impl.scp_read_memory_request \
    import SCPReadMemoryRequest

import sys
import logging

logger = logging.getLogger(__name__)


class IOBufInterface(object):
    """ A thread for reading the IOBUF from a core
    """

    def __init__(self, transceiver, x, y, p, iobuf_address, iobuf_bytes,
                 thread_pool):
        """

        :param transceiver: The transceiver to use to send the message
        :type transceiver: :py:class:`spinnman.transceiver.Transceiver`
        :param x: The x-coordinate of the chip to get the IO Buf from
        :type x: int
        :param y: The y-coordinate of the chip to get the IO Buf from
        :type y: int
        :param iobuf_address: The address of IOBuf in SDRAM
        :type iobuf_address: int
        :param iobuf_bytes: The size of each buffer of iobuf in bytes
        :type iobuf_bytes: int
        :raise None: No known exceptions are thrown
        """
        self._transceiver = transceiver
        self._x = x
        self._y = y
        self._p = p
        self._iobuf_address = iobuf_address
        self._iobuf_bytes = iobuf_bytes

        self._iobuf_condition = Condition()
        self._iobuf = None
        self._exception = None
        self._traceback = None
        self._thread_pool = thread_pool

    def run(self):
        """ Run method of the thread.  Note callers should call start() to\
            actually run this in a separate thread.
        """

        base_address = self._iobuf_address
        iobuf = ""
        try:
            while base_address != 0:

                # Read the first packets worth of data
                first_thread = SCPMessageInterface(
                    self._transceiver, SCPReadMemoryRequest(
                        self._x, self._y, base_address, 256))
                self._thread_pool.apply_async(first_thread.run)
                first_data = first_thread.get_response().data
                reader = LittleEndianByteArrayByteReader(first_data)

                # Read the details of the buffer
                next_base_address = reader.read_int()
                reader.read_int()  # time
                reader.read_int()  # milliseconds
                bytes_to_read = reader.read_int()
                logger.debug("Reading {} bytes of IOBUF, next buffer at {}"
                             .format(bytes_to_read, next_base_address))

                # Read the data out of the packet
                data = reader.read_bytes()
                if bytes_to_read < len(data):
                    iobuf += data[:bytes_to_read].decode("ascii")
                bytes_read = len(data)
                bytes_to_read -= bytes_read
                base_address += bytes_read

                # Read any remaining bytes
                if bytes_to_read > 0:
                    data = self._transceiver.read_memory(
                        self._x, self._y, base_address, bytes_to_read)
                    for data_item in data:
                        iobuf += data_item.decode("ascii")

                base_address = next_base_address

            self._iobuf_condition.acquire()
            self._iobuf = iobuf
            self._iobuf_condition.notify_all()
            self._iobuf_condition.release()
        except Exception as exception:
            self._iobuf_condition.acquire()
            self._exception = exception
            self._traceback = sys.exc_info()[2]
            self._iobuf_condition.notify_all()
            self._iobuf_condition.release()

    def get_iobuf(self):
        """ Get the value of iobuf after it has been retrieved.  This will\
            block until the value has been retrieved
        """
        self._iobuf_condition.acquire()
        while self._iobuf is None and self._exception is None:
            self._iobuf_condition.wait()
        self._iobuf_condition.release()

        if self._exception is not None:
            raise self._exception, None, self._traceback

        return IOBuffer(self._x, self._y, self._p, self._iobuf)
