from enum import auto, Enum
import functools
from threading import Thread
import time
import tkinter as tk
from typing import Tuple
from types import TracebackType

from spinn_utilities.config_holder import get_config_str_or_none
from spinn_utilities.overrides import overrides

from spinn_machine import Machine

from spinnman.connections.udp_packet_connections import (
    SCAMPConnection)
from spinnman.constants import ROUTER_REGISTER_P2P_ADDRESS
from spinnman.data import SpiNNManDataView
from spinnman.exceptions import (
    SpinnmanGenericProcessException, SpinnmanTimeoutException)
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.impl import ReadMemory, GetChipInfo
from spinnman.messages.scp.impl.get_chip_info_response import (
    GetChipInfoResponse)
from spinnman.messages.scp.impl.read_memory import Response
from spinnman.model import P2PTable
from spinnman.processes import (
    MostDirectConnectionSelector)
from spinnman.processes.get_machine_process import (
    GetMachineProcess, P_TO_V_ADDR, P_MAPS_SIZE)
from spinnman.spalloc import SpallocClient, SpallocJob
from spinnman.transceiver import create_transceiver_from_hostname
import spinnman.spinnman_script as sim


class MockJob(object):
    """
    Alernative to Spalloc job when not using spalloc
    """
    def __init__(self, hostname: str) -> None:
        self._hostname = hostname

    @overrides(SpallocJob.get_connections)
    def get_connections(self):
        return {(0, 0): self._hostname}

    @overrides(SpallocJob.create_transceiver)
    def create_transceiver(self, ensure_board_is_ready: bool):
        return create_transceiver_from_hostname(
            hostname = self._hostname,
            ensure_board_is_ready=ensure_board_is_ready)


class State(Enum):
    """
    Different states a Chip could be in
    """
    UNKNOWN = (auto(), "unknown", "snow", " ")
    UNBOOTED_ROOT = (auto(), "root chip", "black", "r")
    UNBOOTED_ETHERNET = (auto(), "ethernet", "gray", "e")
    GETTING_SCAMP = (auto(), "getting scamp", "cyan", "s")
    BOOTING = (auto(), "booting", "slate blue", "b")
    GOT_SCAMP = (auto(), "got scamp", "royal blue", "S")
    CHECKING_CONNECTION = (auto(), "checking connection", "MediumPurple1", "e")
    CHECKED_CONNECTION = (auto(), "checked connection", "purple 1", "E")
    REQUEST_DIMENSIONS = (auto(), "request dimensions", "salmon1", "d")
    GOT_DIMENSIONS = (auto(), "got dimensions", "brown4", "D")
    REQUEST_INF0 = (auto(), "request info", "red", "c")
    GOT_INFO = (auto(), "got info", "orange", "C")
    GOT_MAP = (auto(), "got v tp p map first", "yellow", "C")
    GOT_BOTH = (auto(), "got info and v to p map", "green", "✓")
    REQUESTED_P2P = (auto(), "requested P2P data", "yellow", "r")
    GOT_P2P = (auto(), "got P2P data", "green", "✓")

    def __new__(cls, *args: Tuple[int, str, str, str]) -> 'State':
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(self, value: int, text: str, colour: str, char: str):
        """

        :param value:  ID
        :param text: what str should output
        :param colour:  Background colour
        :param char: text
        """
        # use argument
        _ = value
        self.text = text
        self.colour = colour
        self.char = char

    def __repr__(self) -> str:
        return self.text


class Starter(object):
    """
    Code to Start spinnaker and show steps
    """

    def __init__(self, show_gui: bool) -> None:
        """
        :param show_gui: Flag o say the Gui should show
        """
        self._show_gui = show_gui

        self._chip_states = dict()
        if show_gui:
            self._root = tk.Tk()
            self._root.grid_columnconfigure(1, minsize=700)
            self._root.title("Core states")

            self._status_label = tk.Label(self._root, text="Starting script")
            self._status_label.grid(column=0, row=0)

            frame = tk.Frame(self._root)
            frame.grid(column=0, row=1)
            self._width_label = tk.Label(frame, text="Width = ?")
            self._width_label.grid(column=0, row=0)
            self._height_label = tk.Label(frame, text="Height = ?")
            self._height_label.grid(column=1, row=0)
            self._size_label = tk.Label(frame, text="Unknown")
            self._size_label.grid(column=2, row=0)

            self._chip_frame = tk.Frame(self._root)
            self._chip_frame.grid(column=0, row=2, pady=10)
            self._chip_labels = dict()

            self._column_frame = tk.Frame(self._root)
            self._column_frame.grid(column=0, row=3, pady=10)
            self._columns = dict()

            button = tk.Button(self._root, text='Stop', command=self.close)
            button.grid(column=0, row=4)

        t = Thread(target=self.start_machine)
        t.start()
        if show_gui:
            self._root.mainloop()

    def close(self) -> None:
        """
        Close the qui and end the simulation
        """
        if self._show_gui:
            self._root.destroy()
        sim.end()

    def set_status(self, status: str) -> None:
        """
        Show a status change

        :param status: New status
        """
        print(f"{status=}")
        if self._show_gui:
            self._status_label.configure(text=status)
            self._root.update_idletasks()

    def set_chip(self, x: int, y: int, state: State) -> None:
        """
        Show a state change on a Chio

        :param x: x cooridnate of Chip
        :param y: y coordinate of Chip
        :param state: New state
        """
        if state == State.GOT_INFO:
            if self._chip_states[(x, y)] == State.GOT_MAP:
                state = State.GOT_BOTH
        elif state == State.GOT_MAP:
            if self._chip_states[(x, y)] == State.GOT_INFO:
                state = State.GOT_BOTH
        self._chip_states[(x, y)] = state
        if state != State.UNKNOWN:
            print(f"Chip {x}, {y} {state=}")
        if self._show_gui:
            if x < 255 or y < 255:
                self._chip_labels[(x, y)]["text"] = state.char
                self._chip_labels[(x, y)].config(bg = state.colour)

    def set_column(self, x: int, state: State) -> None:
        """
        Show a state change on a column

        :param x: Column being changed
        :param state: new State
        """
        if state != State.UNKNOWN:
            print(f"Column {x} {state=}")
        if self._show_gui:
            self._columns[x]["text"] = state.char
            self._columns[x].config(bg = state.colour)

    def start_machine(self) -> None:
        """
        Run steps to start a machine

        """
        self.do_setup()
        self.do_grid()
        self.do_transceiver()
        self.do_ensure_board_is_ready()
        self.do_get_machine()
        self.set_status("Finished")

    def do_setup(self) -> None:
        """
        Sets up the simulator and gets a spalloc job

        Uses spinnman.cfg to decide how to get the job

        If a local board is used job with be a Mock
        """
        self.set_status("Setting up")
        sim.setup(n_boards_required=1)

        self.set_status("Checking configuration")
        server = get_config_str_or_none("Machine", "spalloc_server")
        if server is not None:
            self.set_status("Getting Spalloc Client")
            self._client = SpallocClient(
                "https://spinnaker.cs.man.ac.uk/spalloc")

            self.set_status("Getting job")
            self._job = self._client.create_job()

            self.set_status("Waiting for job to be ready")
            self._job.wait_until_ready()
        machine_name = get_config_str_or_none("Machine", "machine_name")
        if machine_name is not None:
            self._job = MockJob(machine_name)

    def do_grid(self) -> None:
        """
        Creates the Chip and Column Gui grids based on connections
        """
        self.set_status("Estimating Machine size")
        width = 0
        height  = 0
        for (x, y) in self._job.get_connections():
            if x > width:
                width = x
            if y > height :
                max_y = y

        version = SpiNNManDataView.get_machine_version()
        w, h = version.board_shape
        width += w
        height += h

        print(f"Estimated {width=} {height=}")
        if self._show_gui:
            self._width_label['text'] = f"{width=}"
            self._height_label['text'] = f"{height=}"
            self._size_label['text'] = f"Estimated"
        # create_grid
        for i in range(width):
            x = i
            for j in range(height):
                y = height - j - 1
                if self._show_gui:
                    self._chip_labels[(x, y)] = tk.Label(self._chip_frame)
                    self._chip_labels[(x, y)].grid(column=i, row=j)
                self.set_chip(x, y, State.UNKNOWN)
            if self._show_gui:
                self._columns[x] = tk.Label(self._column_frame)
                self._columns[x].grid(column=i, row=0)
            self.set_column(x, State.UNKNOWN)

    def do_transceiver(self) -> None:
        """
        Gets a transceiver and record its connections.

        Connections must come from the transceiver and not the job
        as they may be proxied by the Transceiver.
        """
        self.set_status("Create Transceiver")
        self._transceiver = self._job.create_transceiver(
            ensure_board_is_ready=False)

        self.set_status("Getting connections")
        self._scamp_connections = list()
        # print("got connections")
        for conn in list(self._transceiver.get_connections()):
            # print (conn)
            if isinstance(conn, SCAMPConnection):
                self._scamp_connections.append(conn)
                if conn.chip_x == 0 and conn.chip_y == 0:
                    self.set_chip(conn.chip_x, conn.chip_y,
                                  State.UNBOOTED_ROOT)
                else:
                    self.set_chip(conn.chip_x, conn.chip_y,
                                  State.UNBOOTED_ETHERNET)
            #else:
            #     print(type(conn))

    def do_ensure_board_is_ready(self):
        """
        Runs the steps to ensure the transceiver/ boards are ready.
        :return:
        """
        #self._transceiver.ensure_board_is_ready()
        self._try_to_find_scamp_and_boot()
        self._do_get_chip_info()

    def _try_to_find_scamp_and_boot(self) -> None:
        version_info = None
        boot_tries = 0
        rereads = 0
        self.set_chip(0, 0, State.GETTING_SCAMP)
        while version_info is None:
            try:
                self.set_status(f"Get scamp version {boot_tries=} {rereads=}")
                version_info = self._transceiver._get_scamp_version(n_retries=3)
                if version_info.x == 255 and version_info.y == 255:
                    version_info = None
                    rereads += 1
                    time.sleep(0.1)
            except SpinnmanGenericProcessException as e:
                if isinstance(e.exception, SpinnmanTimeoutException):
                    self.set_status(f"boot machine {boot_tries=}")
                    self.set_chip(0, 0, State.BOOTING)
                    self._transceiver._boot_board()
                    self.set_chip(0, 0, State.GETTING_SCAMP)
                    boot_tries += 1
                else:
                    raise
            except SpinnmanTimeoutException:
                self.set_status(f"Boot machine {boot_tries=}")
                self.set_chip(0, 0, State.BOOTING)
                self._transceiver._boot_board()
                self.set_chip(0, 0, State.GETTING_SCAMP)
                boot_tries += 1
        self.set_chip(0, 0, State.GOT_SCAMP)

    def _do_get_chip_info(self) -> None:
        self.set_status("Getting chip info")
        for scamp_connection in self._scamp_connections:
            self._transceiver._change_default_scp_timeout(scamp_connection)
            self.set_chip(scamp_connection.chip_x, scamp_connection.chip_y,
                          State.CHECKING_CONNECTION)
            chip_info = self._transceiver._check_connection(scamp_connection)
            if chip_info is None:
                print(f"No Chip_info for {scamp_connection}")
            else:
                self.set_chip(scamp_connection.chip_x, scamp_connection.chip_y,
                              State.CHECKED_CONNECTION)

    def do_get_machine(self):
        """
        Runs the steps done to get a machine

        """
        self._do_get_machine_dimensions()
        self._do_get_scamp_version()
        self._do_get_machine_process()

    def _do_get_machine_dimensions(self) -> None:
        self.set_status("Getting machine dimensions")
        self.set_chip(0, 0, State.REQUEST_DIMENSIONS)
        self._dimensions = self._transceiver._get_machine_dimensions()
        self.set_chip(0, 0, State.GOT_DIMENSIONS)
        print(f"Dimensions: width={self._dimensions.width} "
              f"height={self._dimensions.height}")
        if self._show_gui:
            self._width_label['text'] = f"width={self._dimensions.width}"
            self._height_label['text'] = f"height={self._dimensions.height}"
            self._size_label['text'] = f"Read"

    def _do_get_scamp_version(self) -> None:
        self.set_status("Getting scamp version")
        self._version_info = self._transceiver._get_scamp_version()

    def _do_get_machine_process(self) -> None:
        self.set_status("Starting Getting machine process")
        connection_selector = MostDirectConnectionSelector(
            self._scamp_connections)
        get_machine_process = VerboseProcess(connection_selector, self)
        machine = get_machine_process.get_machine_details(
            self._version_info.x, self._version_info.y,
            self._dimensions.width, self._dimensions.height)


class VerboseProcess(GetMachineProcess):
    """
    Wrapper around GetMachineProcess to capture requests and responses
    """

    def __init__(self, connection_selector: MostDirectConnectionSelector,
                 gui: Starter) -> None:
        super().__init__(connection_selector)
        self._gui = gui

    @overrides(GetMachineProcess.get_machine_details)
    def get_machine_details(
            self, boot_x: int, boot_y: int,
            width: int, height: int) -> Machine:
        """
        :param boot_x:
        :param boot_y:
        :param width:
        :param height:
        :returns: The Machine read from the boot Chip
        """
        # Get the P2P table - 8 entries are packed into each 32-bit word
        p2p_column_bytes = P2PTable.get_n_column_bytes(height)
        blank = (b'', 0)
        self._p2p_column_data = [blank] * width
        self._gui.set_status("Reading p2p table")
        with self._collect_responses():
            for column in range(width):
                self._gui.set_column(column, State.REQUESTED_P2P)
                offset = P2PTable.get_column_offset(column)
                self._send_request(
                    ReadMemory(
                        coordinates=(boot_x, boot_y, 0),
                        base_address=(ROUTER_REGISTER_P2P_ADDRESS + offset),
                        size=p2p_column_bytes),
                    functools.partial(self._receive_p2p_data, column))
        p2p_table = P2PTable(width, height, self._p2p_column_data)

        self._gui.set_status("Get ChipInfo")
        # Get the chip information for each chip
        with self._collect_responses():
            # Ignore errors, as any error here just means that a chip
            # is down that wasn't marked as down
            for (x, y) in p2p_table.iterchips():
                self._gui.set_chip(x, y, State.REQUEST_INF0)
                self._send_request(GetChipInfo(x, y), self._receive_chip_info)
                self._send_request(
                    ReadMemory((x, y, 0), P_TO_V_ADDR, P_MAPS_SIZE),
                    functools.partial(self._receive_p_maps, x, y))

        self._gui.set_status("Fill Machine")
        version = SpiNNManDataView.get_machine_version()
        machine = version.create_machine(width, height)
        print(machine)
        return self._fill_machine(machine)

    def _receive_p2p_data(
        self, column: int, scp_read_response: Response) -> None:
        self._gui.set_column(column, State.GOT_P2P)
        super()._receive_p2p_data(column, scp_read_response)

    def _receive_chip_info(
            self, scp_read_chip_info_response: GetChipInfoResponse) -> None:
        chip_info = scp_read_chip_info_response.chip_info
        self._gui.set_chip(chip_info.x, chip_info.y, State.GOT_INFO)
        super()._receive_chip_info(scp_read_chip_info_response)

    def _receive_p_maps(
            self, x: int, y: int, scp_read_response: Response) -> None:
        self._gui.set_chip(x, y, State.GOT_MAP)
        super()._receive_p_maps(x, y, scp_read_response)

    def _receive_error(
            self, request: AbstractSCPRequest, exception: Exception,
            tb: TracebackType, connection: SCAMPConnection) -> None:
        print(exception)
        super()._receive_error(request, exception, tb, connection)


def starter_no_gui() -> None:
    """
    Runs the starter with the gui elements off
    :return:
    """
    Starter(show_gui=False)


if __name__ == '__main__':
    # Run the starter with the gui elements on
    Starter(show_gui=True)
