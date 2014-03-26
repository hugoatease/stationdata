#!/usr/bin/env python
from setuptools import setup

setup(
    name='StationData',
    version='0.1',
    description='Library for radio stream metadata fetching',
    author='Hugo Caille',
    license='MIT',

    packages=['stations'],
    install_requires=['requests']
)