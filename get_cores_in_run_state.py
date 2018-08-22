from spinnman.transceiver import create_transceiver_from_hostname
from board_test_configuration import BoardTestConfiguration
from spinn_machine import CoreSubsets, CoreSubset
from spinnman.model.enums import CPUState

board_config = BoardTestConfiguration()
board_config.set_up_remote_board()

# n_cores = 20
core_subsets = CoreSubsets(core_subsets=[])

down_cores = CoreSubsets()
down_chips = CoreSubsets(core_subsets=[])


transceiver = create_transceiver_from_hostname(
    board_config.remotehost, board_config.board_version,
    ignore_cores=down_cores, ignore_chips=down_chips,
    bmp_connection_data=board_config.bmp_names,
    auto_detect_bmp=board_config.auto_detect_bmp)
try:
    count_finished = 0
    count_run = 0
    app_id = 17
    count_finished = transceiver.get_core_state_count(app_id,
                                                      CPUState.FINISHED)
    count_run = transceiver.get_core_state_count(app_id, CPUState.RUNNING)
    print('running: ', count_run, ' finished: ', count_finished)

    machine = transceiver.get_machine_details()
    print('machine max x: ', machine.max_chip_x,
          ' max y: ', machine.max_chip_y)
    print('machine chips: ', machine.chips)

    cores_finished = ()
    all_core_subsets = []
    for chip in machine.chips:
        all_core_subsets.append(CoreSubset(chip.x, chip.y, range(1, 17)))

    all_core_subset = CoreSubsets(
        core_subsets=all_core_subsets)

    cores_finished = transceiver.get_cores_in_state(all_core_subset,
                                                    CPUState.FINISHED)
    cores_running = transceiver.get_cores_in_state(all_core_subset,
                                                   CPUState.RUNNING)
    cores_watchdog = transceiver.get_cores_in_state(all_core_subset,
                                                    CPUState.WATCHDOG)

    for core in cores_running:
        for pid in core.processor_ids:
            if (pid != 0) and (pid != 16):
                print('run core: ', core.x, ' ', core.y, ' ', pid)

    for core in cores_finished:
        for pid in core.processor_ids:
            print('finished core: ', core.x, ' ', core.y, ' ', pid)

    for core in cores_watchdog:
        for pid in core.processor_ids:
            print('watchdog core: ', core.x, ' ', core.y, ' ', pid)

finally:
    transceiver.close()
