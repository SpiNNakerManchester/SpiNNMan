// Copyright (c) 2016 The University of Manchester
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include <spin1_api.h>

void timer_callback(uint unused0, uint unused1) {
    io_printf(IO_BUF, "Hello!\n");
    spin1_exit(0);
}

void c_main(void) {
    io_printf(IO_BUF, "Starting...\n");
    spin1_set_timer_tick(1000);
    spin1_callback_on(TIMER_TICK, timer_callback, 1);
    spin1_start(SYNC_WAIT);
    io_printf(IO_BUF, "Finished\n");
}
