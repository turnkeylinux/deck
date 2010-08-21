import os
import commands

class Error(Exception):
    pass

def _command(command, *args):
    command = command + " " + " ".join([ commands.mkarg(arg) for arg in args])
    
    status, output = commands.getstatusoutput(command)
    if status != 0:
        raise Error("useraufs command failed (%s): %s" % (command, output))

    return output

def is_mounted(path):
    """parse useraufs-show output to determine if <path> is mounted"""
    path = os.path.realpath(path)

    unions = [ line.split("\t") for line in _command("useraufs-show").split("\n") if line ]
    for branches, mnt in unions:
        if mnt == path:
            return True

    return False

def mount(branches, path):
    """useraufs-mount <branch[es]> to <path>
    <branches> can be a tuple, a list or a string."""
    if is_mounted(path):
        return False

    if isinstance(branches, (list, tuple)):
        branches = ":".join(branches)

    _command("useraufs-mount", "--udba=reval", branches, path)
    return True

def umount(path):
    """useraufs-umount <path>"""
    if not is_mounted(path):
        return False

    _command("useraufs-umount", path)
    return True

def remount(operations, path):
    """useraufs-remount <operation[s]> <path>
    <operations> can be a tuple, a list or a string."""
    if isinstance(operations, (list, tuple)):
        operations = ",".join(operations)

    _command("useraufs-remount", operations, path)
