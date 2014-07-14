try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="SpiNNMan",
    version="0.1-SNAPSHOT",
    description="Interaction with a SpiNNaker Machine",
    url="https://github.com/SpiNNakerManchester/SpiNNMan",
    packages=['spinnman'],
    install_requires=['six', 'enum34', 'SpiNNMachine'],
)
