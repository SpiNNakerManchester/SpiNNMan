spinnman.messages.scp_message module
====================================

.. automodule:: spinnman.messages.scp_message

.. currentmodule:: spinnman.messages.scp_message

.. rubric:: Classes

.. autosummary::
    Command
    SCPMessage
    Signal

.. autoclass:: Command
    :show-inheritance:

    .. rubric:: Attributes

    .. autosummary::
        CMD_APLX
        CMD_AR
        CMD_AS
        CMD_FFD
        CMD_FILL
        CMD_FLASH_COPY
        CMD_FLASH_ERASE
        CMD_FLASH_WRITE
        CMD_IPTAG
        CMD_LED
        CMD_LINK_READ
        CMD_LINK_WRITE
        CMD_NNP
        CMD_P2PC
        CMD_POWER
        CMD_READ
        CMD_REMAP
        CMD_RESET
        CMD_RUN
        CMD_SIG
        CMD_SROM
        CMD_TUBE
        CMD_VER
        CMD_WRITE
        RC_ARG
        RC_BUF
        RC_CMD
        RC_CPU
        RC_DEAD
        RC_LEN
        RC_OK
        RC_P2P_BUSY
        RC_P2P_NOREPLY
        RC_P2P_REJECT
        RC_P2P_TIMEOUT
        RC_PKT_TX
        RC_PORT
        RC_ROUTE
        RC_SUM
        RC_TIMEOUT

.. autoclass:: SCPMessage
    :show-inheritance:

    .. rubric:: Attributes

    .. autosummary::
        argument_1
        argument_2
        argument_3
        command
        data
        destination_chip_x
        destination_chip_y
        destination_cpu
        destination_port
        flags
        sequence
        source_chip_x
        source_chip_y
        source_cpu
        source_port
        tag

.. autoclass:: Signal
    :show-inheritance:

    .. rubric:: Attributes

    .. autosummary::
        AND
        CONTINUE
        COUNT
        EXIT
        INITIALISE
        OR
        PAUSE
        POWER_DOWN
        START
        STOP
        SYNC0
        SYNC1
        TIMER
        USER_0
        USER_1
        USER_2
        USER_3

