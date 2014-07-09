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
    array

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

.. autoclass:: array
    :show-inheritance:

    .. rubric:: Attributes

    .. autosummary::
        itemsize
        typecode

    .. rubric:: Methods

    .. autosummary::
        append
        buffer_info
        byteswap
        count
        extend
        fromfile
        fromlist
        fromstring
        fromunicode
        index
        insert
        pop
        read
        remove
        reverse
        tofile
        tolist
        tostring
        tounicode
        write

    .. rubric:: Detailed Methods

    .. automethod:: append
    .. automethod:: buffer_info
    .. automethod:: byteswap
    .. automethod:: count
    .. automethod:: extend
    .. automethod:: fromfile
    .. automethod:: fromlist
    .. automethod:: fromstring
    .. automethod:: fromunicode
    .. automethod:: index
    .. automethod:: insert
    .. automethod:: pop
    .. automethod:: read
    .. automethod:: remove
    .. automethod:: reverse
    .. automethod:: tofile
    .. automethod:: tolist
    .. automethod:: tostring
    .. automethod:: tounicode
    .. automethod:: write

