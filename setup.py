#!/usr/bin/env python
from setuptools import setup

setup(
    name='stationdata',
    version='0.1',
    description='Library for radio stream metadata fetching',
    url='https://github.com/hugoatease/stationdata',
    author='Hugo Caille',
    license='MIT',

    packages=['stations'],
    install_requires=['requests']
)
