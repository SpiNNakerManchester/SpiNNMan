__author__ = 'stokesa6'
import logging

logger = logging.getLogger(__name__)


class AppCalls(object):
    """application specific commands are stored here for clarity"""

    def __init__(self, transceiver):
        """ the app_calls object is used to contain calls which are specific to\
            applications. These can be:\
            \
            loading an application\
            sending app signals \
            app_fill\
            app_stop

            :param transceiver: the parent object which contains other calls
            :type transceiver: spinnman.interfaces.transceiver.Transciever
            :return: a new AppCalls object
            :rtype: spinnman.interfaces.transceiver_tools.app_calls.AppCalls
            :raise: None: does not raise any known exceptions
        """
        pass

    def set_view(self, new_x, new_y, new_cpu, new_node):
        """ updates the chip and processor that is currently under focus

            :param new_x: the new x value of the chip to move focus to
            :param new_y: the new y value of the chip to move focus to
            :param new_cpu: the new p value of the chip to move focus to
            :param new_node: the new x|y|p value to move focus to
            :type new_x: int
            :type new_y: int
            :type new_cpu:int
            :type new_node:int
            :return: None
            :rtype: None
            :raise: None: does not raise any known exceptions
        """
        pass

    def app_load(self, filename, region, cores, app_id, flags=None):
        '''loads a .aplx file onto a collection of cores based off the region\
           given

           :param filename: the file path to a .aplx file to be loaded
           :param region: the region to which the filename will be loaded on\
                          in the board
           :param cores: which cores of the region the filname will be loaded \
                         on in the board
           :param app_id: which application this load is associated with
           :param flags: what behaviour the system should do once the load is \
                         completed
           :type filename: str
           :type region: tuple
           :type cores: str
           :type app_id: int
           :type flags: int or None
           :return: None
           :rtype: None
           :raise:spinnman.spinnman_exceptions.SpinnManException
        '''
        pass

    def app_signal(self, app_id, signal_id, state_id=None, x=None,y=None,
                   range=None):
        """
        :param app_id: the application id that idtnefities which applciation\
                       this signal targets on the machien
        :param signal_id: the type of signal being transmitted to the machine
        :param state_id: the state that processors are in should respond to \
                         this signal
        :param x: the x coord used in region definition
        :param y: the y coord used in region definition
        :param range: a optimial paramter used to calculate a mask for a appid \
                      so that many apps can be signaled with the same message
        :type app_id: int
        :type signal_id: int or string
        :type state_id: int or string
        :type x: int
        :type y: int
        :type range: str
        :return: None
        :rtype: None
        :raise:spinnman.spinnman_exceptions.SpinnManException, \
               spinnman.spinnman_exceptions.InvalidSignal, \
               spinnman.spinnman_exceptions.InvalidState
        """
        pass