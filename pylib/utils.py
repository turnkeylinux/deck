# Copyright (c) TurnKey Linux - http://www.turnkeylinux.org
#
# This file is part of Deck
#
# Deck is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.

import os
import errno
from os.path import *

def make_relative(root, path):
    """Return <path> relative to <root>.

    For example:
        make_relative("../../", "file") == "path/to/file"
        make_relative("/root", "/tmp") == "../tmp"
        make_relative("/root", "/root/backups/file") == "backups/file"
        
    """

    up_count = 0

    root = realpath(root).rstrip('/')
    path = realpath(path).rstrip('/')

    while True:
        if path == root or path.startswith(root.rstrip("/") + "/"):
            return ("../" * up_count) + path[len(root) + 1:]

        root = dirname(root).rstrip('/')
        up_count += 1

def makedirs(path):
    try:
        os.makedirs(path)
    except OSError, e:
        if e[0] != errno.EEXIST:
            raise
