import logging

logger = logging.getLogger(__name__)


class _AppCalls(object):
    """ Commands that deal with executables
    """

    def __init__(self, transceiver):
        """
        :param transceiver: the parent object which contains other calls
        :type transceiver: spinnman.transceiver.Transciever
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

    def load_executable(self, executable_data_item, app_id):
        """ Loads an executable on to a set of cores

        :param executable_data_item: An implementation of\
                     AbstractExecutableDataItem detailing what to load
        :type executable_data_item: spinnman.abstract_executable_data_item.AbstractExecutableDataItem
        :param app_id: The id of the application > 0
        :type app_id: int
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanReadException: If there is an error\
                    reading the executable
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    app_id is not a valid application id
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response is received during the transaction that is\
                    unexpected
        """
        pass

    def send_signal(self, app_id, signal, chips_and_cores=None, state=None):
        """ Sends a signal to an application running on the board 
        
        :param app_id: The application id that identifies which application\
                       this signal targets on the machine
        :type app_id: int
        :param signal: The signal to send
        :type signal: SIGNAL
        :param chips_and_cores: An optional list of chips and cores on each\
                    chip where the signal is to be sent, as a tuple of\
                    (x, y, list of cores), where x is the x-coordinate of a\
                    chip, y is the y-coordinate of a chip and list of cores is\
                    a list of processor ids on that chip.  If not specified,\
                    the signal is sent to all cores which are running the app
        :type chips_and_cores: list of tuples of (int, int, list of int)
        :param state: If specified, the signal is only sent to cores which are\
                    currently in this state
        :type state: STATE
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:\
                      * If the app_id is not a valid value
                      * If the the signal is not a valid signal id
                      * If one of the chip or core ids is invalid
                      * If the state is not a valid state
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response is received during the transaction that is\
                    unexpected
        """
        pass
