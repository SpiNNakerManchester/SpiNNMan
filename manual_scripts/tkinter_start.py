from threading import Thread
import tkinter as tk

from spinn_utilities.config_holder import get_config_str_or_none
from spinnman.connections.udp_packet_connections import (
    BootConnection, SCAMPConnection)
from spinnman.data import SpiNNManDataView
from spinnman.spalloc import SpallocClient, SpallocJob
from spinnman.transceiver import create_transceiver_from_hostname

import spinnman.spinnman_script as sim

class NoJob(object):
    def __init__(self, hostname: str) -> None:
        self._hostname = hostname

    def get_connections(self):
        return {(0, 0): self._hostname}

    def create_transceiver(self, ensure_board_is_ready: bool):
        return create_transceiver_from_hostname(
            hostname = self._hostname,
            ensure_board_is_ready=ensure_board_is_ready)

class CoreCounter(object):

    def __init__(self) -> None:
        self._labels = dict()
        self._boot_tries = 0

        self._root = tk.Tk()
        self._root.grid_columnconfigure(1, minsize=700)
        self._root.title("Core states")
        self._status_label = tk.Label(self._root, text="Starting script")
        self._status_label.grid(column=0, row=0)
        self._core_frame = tk.Frame(self._root)
        self._core_frame.grid(column=0, row=1)
        #button = tk.Button(self._root, text='Run', command=self.do_run)
        #button.grid(column=0, row=2)
        button = tk.Button(self._root, text='Stop', command=self.close)
        button.grid(column=0, row=2)
        t = Thread(target=self.do_setup)
        t.start()
        self._root.mainloop()

    def close(self) -> None:
        self._root.destroy()
        sim.end()

    def set_status(self, status: str) -> None:
        print(f"{status=}")
        self._status_label.configure(text=status)
        self._root.update_idletasks()

    def do_setup(self) -> None:
        self.set_status("Setting up")
        sim.setup(n_boards_required=1)
        t = Thread(target=self.check_cfg)
        t.start()

    def check_cfg(self) -> None:
        self.set_status("Checking configuration")
        server = get_config_str_or_none("Machine", "spalloc_server")
        if server is not None:
            t = Thread(target=self.do_client)
            t.start()
        machine_name = get_config_str_or_none("Machine", "machine_name")
        if machine_name is not None:
            self._job = NoJob(machine_name)
            t = Thread(target=self.do_grid)
            t.start()

    def do_client(self) -> None:
        self.set_status("Getting Spalloc Client")
        self._client = SpallocClient("https://spinnaker.cs.man.ac.uk/spalloc")
        t = Thread(target=self.do_job)
        t.start()

    def do_job(self) -> None:
        self.set_status("Getting job")
        self._job = self._client.create_job()
        t = Thread(target=self.do_job_ready)
        t.start()

    def do_job_ready(self) -> None:
        self.set_status("Waiting for job to be ready")
        self._job.wait_until_ready()
        t = Thread(target=self.do_grid)
        t.start()

    def do_grid(self) -> None:
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

        # create_grid
        for i in range(width):
            x = i
            for j in range(height):
                y = height - j - 1
                self._labels[(x, y)] = tk.Label(self._core_frame, text=f"{x}{y}",
                                                bg="White")
                self._labels[(x, y)].grid(column=i, row=j)

        t = Thread(target=self.do_tranceiver)
        t.start()

    def do_tranceiver(self) -> None:
        self.set_status("Create Transceiver")
        self._transceiver = self._job.create_transceiver(
            ensure_board_is_ready=False)
        t = Thread(target=self.do_connections)
        t.start()

    def do_connections(self) -> None:
        self.set_status("Getting connections")
        self._scamp_connections = list()
        print("got connections")
        for conn in list(self._transceiver.get_connections()):
            print (conn)
            if isinstance(conn, BootConnection):
                self._boot_send_connection = conn
                self._labels[(0, 0)]['text'] = "B"
            # Locate any connections that talk to a BMP
            elif isinstance(conn, SCAMPConnection):
                self._scamp_connections.append(conn)
                if conn.chip_x == 0 and conn.chip_y == 0:
                    self._root_connection = conn
                    self._labels[(conn.chip_x, conn.chip_y)]['text'] = "R"
                elif conn.chip_x == 255 and conn.chip_y == 255:
                    pass
                else:
                    self._labels[(conn.chip_x, conn.chip_y)]['text'] = "E"
            else:
                print(type(conn))
        t = Thread(target=self.do_scamp_version)
        t.start()

    def do_scamp_version(self ) -> None:
        self._boot_tries += 100
        self.set_status(f"Check scamp version {self._boot_tries}")
        version_info = self._transceiver._get_scamp_version()
        print(f"{version_info=}")
        if version_info is None:
            print("version info is None")
            t = Thread(target=self.do_boot_board)
            t.start()
        else:
            print("version info not None")
            t = Thread(target=self.done)
            t.start()

    def do_boot_board(self) -> None:
        self.set_status(f"Booting board {self._boot_tries}")
        self._boot_tries += 1
        try:
            self._transceiver._boot_board()
        except Exception as ex:
            print(type(ex))
        t = Thread(target=self.do_scamp_version)
        t.start()

    def done(self) -> None:
        self.set_status("Finished")


core_counter = CoreCounter()
