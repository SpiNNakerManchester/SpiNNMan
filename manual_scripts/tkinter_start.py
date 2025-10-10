import tkinter as tk
from typing import Tuple

from spinnman.connections.udp_packet_connections import (
    BootConnection, SCAMPConnection)
from spinnman.spalloc import SpallocClient, SpallocJob
import spinnman.spinnman_script as sim


class CoreCounter(object):

    def __init__(self) -> None:
        self._labels = dict()
        self._boot_tries = 0

        self._root = tk.Tk()
        self._root.title("Core states")
        self._status_label = tk.Label(self._root, text="Starting script")
        self._status_label.grid(column=0, row=0)
        self._core_frame = tk.Frame(self._root)
        self._core_frame.grid(column=0, row=1)
        #button = tk.Button(self._root, text='Run', command=self.do_run)
        #button.grid(column=0, row=2)
        button = tk.Button(self._root, text='Stop', command=self.close)
        button.grid(column=0, row=2)
        self._root.after(0, self.do_setup)
        self._root.mainloop()

    def close(self) -> None:
        self._root.destroy()
        sim.end()

    def set_status(self, status: str) -> None:
        print(status)
        self._status_label.configure(text=status)
        self._root.update_idletasks()

    def do_setup(self) -> None:
        self.set_status("Setting up")
        sim.setup(n_boards_required=1)
        self._root.after(0, self.do_client)

    def do_client(self) -> None:
        self.set_status("Getting Spalloc Client")
        self._client = SpallocClient("https://spinnaker.cs.man.ac.uk/spalloc")
        self._root.after(0, self.do_job)

    def do_job(self) -> None:
        self.set_status("Getting job")
        self._job = self._client.create_job()
        self._root.after(0, self.do_job_ready)

    def do_job_ready(self) -> None:
        self.set_status("Waiting for job to be ready")
        self._job.wait_until_ready()
        self._root.after(0, self.do_grid)

    def do_grid(self) -> None:
        self.set_status("Estimating Machine size")
        width = 0
        height  = 0
        for (x, y) in self._job.get_connections():
            if x > width:
                width = x
            if y > height :
                max_y = y
        width += 8
        height += 8

        # create_grid
        for i in range(width):
            x = i
            for j in range(height):
                y = height - j - 1
                self._labels[(x, y)] = tk.Label(self._core_frame, text=f"{x}{y}",
                                                bg="White")
                self._labels[(x, y)].grid(column=i, row=j)

        self._root.after(0, self.do_tranceiver)

    def do_tranceiver(self) -> None:
        self.set_status("Create Transceiver")
        self._transceiver = self._job.create_transceiver(
            ensure_board_is_ready=False)
        self._root.after(0, self.do_connections)

    def do_connections(self) -> None:
        self.set_status("Getting connections")
        self._scamp_connections = list()
        print("got connections")
        for conn in list(self._transceiver.get_connections()):
            print (conn)
            if isinstance(conn, BootConnection):
                self._boot_send_connection = conn
            # Locate any connections that talk to a BMP
            elif isinstance(conn, SCAMPConnection):
                self._scamp_connections.append(conn)
                if conn.chip_x == 0 and conn.chip_y == 0:
                    self._root_connection = conn
                    self._labels[(conn.chip_x, conn.chip_y)]['text'] = "R"
                else:
                    self._labels[(conn.chip_x, conn.chip_y)]['text'] = "E"
            else:
                print(type(conn))
            self._root.after(0, self.do_scamp_version)

    def do_scamp_version(self ) -> None:
        self.set_status("Check scamp version")
        version_info = self._transceiver._get_scamp_version()
        if version_info is None:
            self._root.after(0, self.do_boot_board)
        else:
            self._root_after(0, self.done)

    def do_boot_board(self) -> None:
        self.set_status("Booting board")
        self._boot_tries += 1
        try:
            self._transceiver._boot_board()
        except Exception as ex:
            print(type(ex))
        self._root.after(0, self.do_scamp_version)

    def done(self) -> None:
        self.set_status("Finished")


core_counter = CoreCounter()
