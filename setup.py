try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="SpiNNMan",
    version="2015.003-rc-01",
    description="Interaction with a SpiNNaker Machine",
    url="https://github.com/SpiNNakerManchester/SpiNNMan",
    license="GNU GPLv3.0",
    packages=['spinnman',
              'spinnman._threads',
              'spinnman.connections',
              'spinnman.connections.abstract_classes',
              'spinnman.connections.abstract_classes.udp_receivers',
              'spinnman.connections.abstract_classes.udp_senders',
              'spinnman.connections.listeners',
              'spinnman.connections.listeners.queuers',
              'spinnman.connections.udp_packet_connections',
              'spinnman.data',
              'spinnman.messages',
              'spinnman.messages.eieio',
              'spinnman.messages.scp',
              'spinnman.messages.scp.abstract_messages',
              'spinnman.messages.scp.impl',
              'spinnman.messages.sdp',
              'spinnman.messages.spinnaker_boot',
              'spinnman.messages.spinnaker_boot._system_variables',
              'spinnman.messages.udp_utils',
              'spinnman.model'],
    package_data={'spinnman.messages.spinnaker_boot': ['boot_data/*.boot']},
    install_requires=['six', 'enum34', 'SpiNNMachine >= 2015.003-rc-01']
)
