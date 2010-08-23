from os.path import *

import re
import sys
import subprocess
import types

from StringIO import StringIO

class Error(Exception):
    pass

def is_mounted(dir):
    return Mounts("/proc/mounts").exists(realpath(dir))

def system(*args):
    error = subprocess.call(args)
    if error:
        raise Error("nonzero exitcode %d from command `%s'" % (error, " ".join(args)))

class Mount:
    def __init__(self, device, dir, type, opts):
        self.device = device
        self.dir = dir
        self.type = type
        self.opts = opts
        
    def mount(self, root):
        if self.is_mounted(root):
            return False
        
        if root:
            realdir = root + self.dir
        else:
            realdir = self.dir

        system("mount", "-t", self.type, "-o", self.opts, self.device, realdir)
        return True

    def umount(self, root):
        if not self.is_mounted(root):
            return False
        
        if root:
            realdir = root + self.dir
        else:
            realdir = self.dir
        system("umount", realdir)
        return True

    def is_mounted(self, root):
        if root:
            realdir = root + self.dir
        else:
            realdir = self.dir
        return is_mounted(realdir)

class Mounts:
    def __init__(self, fstab, root=None):
        """Initialize mounts from <fstab>, which can be a file path, a file handle,
        or a string containing fstab-like values.
        
        if <root> is specified, filter mounts to submounts under the root"""

        self.mounts = []
        if isinstance(fstab, file):
            fh = fstab
        else:
            fstab = str(fstab)
            if exists(fstab):
                try:
                    fh = file(fstab)
                except IOError, e:
                    raise Error(e)
            else:
                fh = StringIO(fstab)

        if root:
            root = realpath(root)
        
        for line in fh.readlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            vals = re.split(r'\s+', line)
            if len(vals) < 4:
                continue

            device, dir, type, opts = vals[:4]
            if not dir.startswith("/"):
                dir = "/" + dir
                
            if root:
                dir = realpath(dir)
                # skip mounts that arne't subdirectories of root
                if dir == root or not dir.startswith(root + "/"):
                    continue

                if root != "/":
                    dir = dir[len(root):]

            mount = Mount(device, dir, type, opts)
            self.mounts.append(mount)

        self.root = root

    def __len__(self):
        return len(self.mounts)
    
    def __str__(self):
        return "\n".join([ " ".join([mount.device, mount.dir, mount.type, mount.opts]) \
                           for mount in self.mounts ])
    
    def save(self, path):
        fh = file(path, "w")
        print >> fh, str(self)
        fh.close()

    def exists(self, dir):
        """Returns True if dir exists in mounts"""
        for mount in self.mounts:
            if mount.dir.rstrip("/") == dir.rstrip("/"):
                return True
        return False

    def mount(self, root=None):
        if root is None:
            root = self.root
            
        for mount in self.mounts:
            mount.mount(root)

    def umount(self, root=None):
        if root is None:
            root = self.root

        for mount in reversed(self.mounts):
            mount.umount(root)
