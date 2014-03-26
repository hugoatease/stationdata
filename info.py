#!/usr/bin/python
from sys import argv
from stations import fetch

print fetch(argv[-1])