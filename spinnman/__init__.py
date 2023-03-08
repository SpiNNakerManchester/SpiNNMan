# Copyright (c) 2014 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Used to communicate with a SpiNNaker Board. The main part of this package is
the :py:class:`~spinnman.transceiver.Transceiver` class. This can be used to
send and receive packets in various SpiNNaker formats, depending on what
connections are available.

Functional Requirements
=======================

#. *Connect* to and communicate with a machine using a number of different
   connections.

#. *Boot* a machine with the expected version of the software.

   * If the machine is already booted but the version is not the version
     expected, an exception will be thrown.

#. *Check the version* of the software which the machine is booted with.

#. *Query the state* of the machine to determine:

   * What the current state of the machine is in terms of the chips and cores
     available, the SDRAM available on the chips and which links are available
     between which chips.

   * What external links to the host exist (and separately add the discovered
     links to the set of links used to communicate with the machine).

   * What is running on the machine and where, and what the current status of
     those processes are.

   * How many cores are in a given state.

   * What is in the IOBUF buffers.

   * What the current routing entries for a given router are.

   * What the routing status counter values are.

#. *Load application binaries* on to the machine, either to individual cores or
   via a "flood-fill" mechanism to multiple cores simultaneously (which may be
   a subset of the cores on a subset of the chips).

#. *Write data to SDRAM*, either on an individual chip, or via a "flood-fill"
   mechanism to multiple chips simultaneously.

#. Send a *signal* to an application.

#. *Read data from SDRAM* on an individual chip.

#. *Send and receive SpiNNaker packets* where the connections allow this.

   * If no connection supports this packet type, an exception is thrown.

   * The user should be able to select which connection is used. Selection of a
     connection which does not support the traffic type will also result in an
     exception.

#. *Send and receive SCP and SDP* packets where the connections allow this.

   * If no connection supports the packet type, an exception is thrown.

   * The user should be able to select which connection is used. Selection of a
     connection which does not support the traffic type will also result in an
     exception.

#. It should be possible to *call* any of the functions *simultaneously,*
   including the same function more than once.

   * Where possible, multiple connections should be used to overlap calls.

   * The functions should not return until they have confirmed that any
     messages sent have been received, and any responses have been received.

   * Functions should not respond with the result of a different function.

   * Functions can further sub-divide the call into a number of separate calls
     that can be divided across the available connections, so long as the other
     requirements are met.

#. *More than one machine* can be connected to the same host.

   * Once the subset of connections has been worked out for each machine, the
     operation of these machines should be independent.

Use Cases
=========

* Connecting is done by using
  :py:func:`~spinnman.transceiver.create_transceiver_from_hostname`.

* :py:meth:`~spinnman.transceiver.Transceiver.boot_board` and
  :py:meth:`~spinnman.transceiver.Transceiver.get_scamp_version` are used to
  ensure that the board is booted correctly before starting a simulation.

* :py:meth:`~spinnman.transceiver.Transceiver.get_machine_details` is used to
  get a representation of the current state of the machine, which is used to
  decide where executables are to be run on the board for a particular
  simulation, where any external peripherals are connected, and how messages
  between the executables and/or the external peripherals are to be routed.

* :py:meth:`~spinnman.transceiver.Transceiver.write_memory` and
  :py:meth:`~spinnman.transceiver.Transceiver.execute` are used to write
  parameters and execute executables on the board

* :py:meth:`~spinnman.transceiver.Transceiver.send_signal` is used to send a
  signal which starts, stops or pauses a simulation.

* :py:meth:`~spinnman.transceiver.Transceiver.get_core_state_count` is used to
  determine if a simulation is complete or has gone into an error state.

* :py:meth:`~spinnman.transceiver.Transceiver.get_iobuf`,
  :py:meth:`~spinnman.transceiver.Transceiver.get_cpu_information` and
  :py:meth:`~spinnman.transceiver.Transceiver.get_router_diagnostics` are used
  to diagnose a problem with a simulation.

* :py:meth:`~spinnman.transceiver.Transceiver.read_memory` is used to read some
  statistics recorded in SDRAM after a simulation.
"""
from spinnman._version import __version__  # NOQA
from spinnman._version import __version_name__  # NOQA
from spinnman._version import __version_month__  # NOQA
from spinnman._version import __version_year__  # NOQA
