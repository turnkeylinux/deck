# Copyright (c) TurnKey GNU/Linux - http://www.turnkeylinux.org
#
# This file is part of Deck
#
# Deck is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.

import os
import commands

from executil import getoutput as command

def is_mounted(path):
    """parse useraufs-show output to determine if <path> is mounted"""
    path = os.path.realpath(path)

    unions = [ line.split("\t") for line in command("useraufs-show").split("\n") if line ]
    for branches, mnt in unions:
        if mnt == path:
            return True

    return False

def mount(branches, path):
    """useraufs-mount <branch[es]> to <path>
    <branches> can be a tuple, a list or a string."""
    if is_mounted(path):
        return False

    if not isinstance(branches, (list, tuple)):
        branches = [ branches ]
        
    command("useraufs-mount", "--udba=reval", path, *branches)
    return True

def umount(path):
    """useraufs-umount <path>"""
    if not is_mounted(path):
        return False

    command("useraufs-umount", path)
    return True

def remount(operations, path):
    """useraufs-remount <operation[s]> <path>
    <operations> can be a tuple, a list or a string."""
    if not isinstance(operations, (list, tuple)):
        operations = [ operations ]

    command("useraufs-remount", path, *operations)
