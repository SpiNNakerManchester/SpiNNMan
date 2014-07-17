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
            'spinnman.messages.spinnaker_boot',
            'spinnman.messages.spinnaker_boot._system_variables'
            'spinnman.model'],
    package_data={'spinnman.messages.spinnkaer_boot', ['boot_data/*.boot']},
    install_requires=['six', 'enum34', 'SpiNNMachine']
)
