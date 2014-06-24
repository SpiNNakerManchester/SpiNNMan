__author__ = 'stokesa6'

import socket
import struct
import threading
import thread
import time
import logging
import traceback
from spinnman.interfaces.port_listeners.port_queuer import _PortQueuer


logger = logging.getLogger(__name__)


def _timeout(visualiser, timeout):
    time.sleep(timeout)
    visualiser.stop()

DEBUG = "FALSE"


class PortListener(threading.Thread):
    """used to listen to a given port"""

    def __init__(self, machine_time_step, time_scale_factor):
        """
        :param machine_time_step: the machine time step (how quickly tics hapen)
        :param time_scale_factor: how much real time is each time tic slowed \
                                  down by
        :type machine_time_step: int
        :type time_scale_factor: int
        
        :return a new PortListener object
        :rtype: spinnman.interfaces.port_listener.PortListener object
        :raise socket errors: when something fails in creating a socket
        """
        threading.Thread.__init__(self)
        self._machine_time_step = machine_time_step
        self._time_scale_factor = time_scale_factor
        self._iptag_map = dict()
        self._done = False
        self._bufsize = None
        self._queuer = _PortQueuer()
        #used in fake packets or debugs
        self._packet_count = 0

    def add_page_listener(self, iptag, listener):
        """supports front ends connecting iptags to given pages

        :param iptag: the associated iptag used for listening
        :param listener: the method to call when packets are reciecved with \
                         the assoicated iptag.
        :type iptag: spinnman.interfaces.iptag
        :type listener: function method / instance method
        :return: None
        :rtype: None
        :raise None:  does not raise any known exceptions
        """
        if iptag not in self._iptag_map.keys():
            self._iptag_map[iptag] = list()
        self._iptag_map[iptag].append(listener)

    def set_timeout(self, timeout):
        """supports changing how long to timeout

        :param timeout: the associated length of time for a timeout
        :type timeout: int
        :return: None
        :rtype: None
        :raise None:  does not raise any known exceptions
        """
        print("Timeout set to %f" % timeout)
        if timeout > 0:
            thread.start_new_thread(_timeout, (self, timeout))
            self._queuer.set_timeout(timeout)

    def set_bufsize(self, bufsize):
        """supports changing of the bufsize

        :param bufsize: the associated new bufsize
        :type bufsize: int
        :return: None
        :rtype: None
        :raise None:  does not raise any known exceptions
        """
        self._bufsize = bufsize

    def stop(self):
        """stops the port listener

        :return: None
        :rtype: None
        :raise None:   does not raise any known exceptions
        """
        logger.info("[port_listener] Stopping")
        self._queuer.stop()
        self._done = True

    def set_port(self, port):
        """sets the listeners port

        :return: None
        :rtype: None
        :raise None:   does not raise any known exceptions
        """
        self._queuer.set_port(port)

    def run(self):
        """opening method for this thread

        :return: None
        :rtype: None
        :raise None:   does not raise any known exceptions

        """
        logger.info("[port_listener] starting")
        self._queuer.start()
        t_tic = 0
        if DEBUG == "FALSE":
            self._packet_count = 0

        while not self._done:
            try:
                if DEBUG == "FALSE":
                    #print "trying to recive"
                    data = self._queuer.get_packet()
                    # print "received"
                    (ip_time_out_byte, pad_byte, flags_byte, tag_byte,
                     dest_port_byte, source_port_byte, dest_addr_short,
                     source_addr_short, command_short, sequence_short,
                     arg1_int, arg2_int, arg3_int) =\
                        struct.unpack_from("<BBBBBBHHHHiii", data, 0)
                    header_length = 26
                    spikedatalen = len(data) - header_length
                    t_tic = arg1_int

                    for spike in range(0, spikedatalen, 4):
                        spike_word = \
                            struct.unpack_from("<I", data,
                                               spike + header_length)[0]
                        for listener_method in self._iptag_map[tag_byte]:
                            listener_method(spike_word)
                else:  # create fake spikes
                    t_tic = self._generate_fake_spikes(t_tic)

            except socket.timeout:
                pass
            except Exception as e:
                if not self._done:
                    traceback.print_exc()
                    logger.debug("[visualiser_listener] Error "
                                 "receiving data: %s" % e)

    def _generate_fake_spikes(self, t_tic):
        """helper method for generating spikes

        :param t_tic: the current timer tic
        :type t_tic: int
        :return: next time tic
        :rtype: int
        :raise None:  does not raise any known exceptions
        """
        time.sleep(0.1)
        x = 0
        y = 0
        p = 2
        nid = self._packet_count
        spike_word = x << 24 | y << 16 | p - 1 << 11 | nid

        self._packet_count += 1
        if self._packet_count >= 100:
            self._packet_count = 0

        for listener_key in self._iptag_map.keys():
            for listener_method in self._iptag_map[listener_key]:
                listener_method(spike_word)
        t_tic += 1
        return t_tic