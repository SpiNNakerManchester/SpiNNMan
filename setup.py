try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="SpiNNMan",
    version="2015.004.01",
    description="Interaction with a SpiNNaker Machine",
    url="https://github.com/SpiNNakerManchester/SpiNNMan",
    license="GNU GPLv3.0",
    packages=['spinnman',
              'spinnman.connections',
              'spinnman.connections.abstract_classes',
              'spinnman.connections.udp_packet_connections',
              'spinnman.data',
              'spinnman.messages',
              'spinnman.messages.eieio',
              'spinnman.messages.eieio.abstract_messages',
              'spinnman.messages.eieio.command_messages',
              'spinnman.messages.eieio.data_messages',
              'spinnman.messages.eieio.data_messages.eieio_16bit',
              'spinnman.messages.eieio.data_messages.eieio_16bit_with_payload',
              'spinnman.messages.eieio.data_messages.eieio_32bit',
              'spinnman.messages.eieio.data_messages.eieio_32bit_with_payload',
              'spinnman.messages.scp',
              'spinnman.messages.scp.abstract_messages',
              'spinnman.messages.scp.impl',
              'spinnman.messages.sdp',
              'spinnman.messages.spinnaker_boot',
              'spinnman.messages.spinnaker_boot._system_variables',
              'spinnman.model',
              'spinnman.model_binaries',
              'spinnman.processes',
              'spinnman.utilities'],
    package_data={'spinnman.messages.spinnaker_boot': ['boot_data/*.boot'],
                  'spinnman.model_binaries': ['*.aplx']},
    install_requires=['six', 'enum34', 'SpiNNMachine == 2015.004.01']
)
