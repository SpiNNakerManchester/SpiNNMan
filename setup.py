try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="SpiNNMan",
    version="0.1-SNAPSHOT",
    description="Interaction with a SpiNNaker Machine",
    url="https://github.com/SpiNNakerManchester/SpiNNMan",
    packages=['spinnman',
            'spinnman.connections',
            'spinnman.data',
            'spinnman.messages',
            'spinnman.messages.scp',
            'spinnman.messages.scp.impl',
            'spinnman.messages.sdp',
            'spinnman.model'],
    install_requires=['six', 'enum34', 'SpiNNMachine']
)
