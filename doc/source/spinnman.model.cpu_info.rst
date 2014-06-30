spinnman.model.cpu_info module
==============================

.. automodule:: spinnman.model.cpu_info

.. currentmodule:: spinnman.model.cpu_info

.. rubric:: Classes

.. autosummary::
    CPUInfo
    MailboxCommands
    RunTimeError
    State

.. autoclass:: CPUInfo
    :show-inheritance:

    .. rubric:: Attributes

    .. autosummary::
        application_id
        application_mailbox_command
        application_mailbox_data_address
        application_name
        iobuf_address
        link_register
        monitor_mailbox_command
        monitor_mailbox_data_address
        p
        processor_state_register
        registers
        run_time_error
        software_error_count
        software_source_filename
        software_source_line_number
        stack_pointer
        state
        time
        user
        x
        y

.. autoclass:: MailboxCommands
    :show-inheritance:

    .. rubric:: Attributes

    .. autosummary::
        SHM_CMD
        SHM_IDLE
        SHM_MSG
        SHM_NOP
        SHM_SIGNAL

.. autoclass:: RunTimeError
    :show-inheritance:

    .. rubric:: Attributes

    .. autosummary::
        ABORT
        DABT
        DIVBY0
        EVENT
        FIQ
        IOBUF
        IRQ
        MALLOC
        NONE
        PABT
        RESET
        SVC
        SWERR
        UNDEF
        VIC

.. autoclass:: State
    :show-inheritance:

    .. rubric:: Attributes

    .. autosummary::
        C_MAIN
        DEAD
        FINSHED
        IDLE
        INITIALISING
        PAUSED
        POWERED_DOWN
        READY
        RUNNING
        RUN_TIME_EXCEPTION
        SYNC0
        SYNC1
        WATCHDOG

