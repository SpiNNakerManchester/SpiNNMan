__author__ = 'stokesa6'
import logging

logger = logging.getLogger(__name__)


class _AppCalls(object):
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
            :rtype: spinnman.interfaces.transceiver_tools.app_calls._AppCalls
            :raise None: does not raise any known exceptions
        """
        self._signal_states = {0: 'init', 1: 'pwrdn', 2: 'stop', 3: 'start',
                              4: 'sync0', 5: 'sync1', 6: 'pause', 7: 'cont',
                              8: 'exit', 9: 'timer', 10: 'usr0', 11: 'usr1',
                              12: 'usr2', 13: 'usr3', 16: 'or', 17: 'and',
                              18: 'count'}
        self._states = {0: 'dead', 1: 'pwrdn', 2: 'rte', 3: 'wdog', 4: 'init',
                       5: 'ready', 6: 'c_main', 7: 'run', 8: 'sync0',
                       9: 'sync1', 10: 'pause', 11: 'exit', 15: 'idle'}
        self._sig_type = {'init': 2, 'pwrdn': 2, 'stop': 2, 'start': 2,
                         'sync0': 0, 'sync1': 0, 'pause': 0, 'cont': 0,
                         'exit': 2, 'timer': 0, 'usr0': 0, 'usr1': 0,
                         'usr2': 0, 'usr3': 0, 'or': 1, 'and': 1, 'count': 1}

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
           :raise spinnman.exceptions.SCPError: whens an error occurs \
                                                  at the connection level
        '''
        pass

    def app_signal(self, app_id, signal_id, state_id=None, x=None,y=None,
                   range=None):
        """sends a signal to the board 
        
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
        :raise spinnman.exceptions.SCPError: whens an error occurs at\
                                                      the connection level
        :raise spinnman.exceptions.InvalidSignalException: when the signal sent\
                                           is not a valid signal id
        :raise spinnman.exceptions.InvalidStateException: when the state sent \
                                          is not a valid state id
        """
        pass