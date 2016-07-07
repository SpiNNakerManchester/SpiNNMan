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
