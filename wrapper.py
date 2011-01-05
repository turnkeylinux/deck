#!/usr/bin/python
# Copyright (c) 2010 TurnKey Linux - all rights reserved
from os.path import *
import pyproject

class CliWrapper(pyproject.CliWrapper):
    INSTALL_PATH = dirname(__file__)

if __name__=='__main__':
    CliWrapper.main()

