// Copyright (c) 2017-2019 The University of Manchester
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

#include <spin1_api.h>

void timer_callback(uint unused0, uint unused1) {
    io_printf(IO_BUF, "Hello!\n");
    spin1_exit(0);
}

void c_main() {
    io_printf(IO_BUF, "Starting...\n");
    spin1_set_timer_tick(1000);
    spin1_callback_on(TIMER_TICK, timer_callback, 1);
    spin1_start(SYNC_WAIT);
    io_printf(IO_BUF, "Finished\n");
}
