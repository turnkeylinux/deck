import re

def is_mounted(dir):
    return Mounts("/proc/mounts").exists(dir)
    
class Mount:
    def __init__(self, device, dir, type, opts):
        self.device = device
        self.dir = dir
        self.type = type
        self.opts = opts
        
    def mount(self, root):
        if root:
            realdir = root + self.dir
        else:
            realdir = self.dir

        command = "mount -t %s -o %s %s %s" % (self.type, self.opts, self.device, realdir)
        print command

    def umount(self, root):
        if root:
            realdir = root + self.dir
        else:
            realdir = self.dir
        command = "umount %s" % realdir
        print command

    def is_mounted(self, root):
        if root:
            realdir = root + self.dir
        else:
            realdir = self.dir
        return is_mounted(realdir)

class Mounts:
    def __init__(self, fstab, root=None):
        """Initialize mounts from fstab.
        if 'root' is specified, filter mounts to submounts under the root"""

        self.mounts = []
        for line in file(fstab).readlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            vals = re.split(r'\s+', line)
            if len(vals) < 4:
                continue

            device, dir, type, opts = vals[:4]
            if root:
                # skip mounts that arne't subdirectories of root
                if dir == root or not dir.startswith(root + "/"):
                    continue

                if root != "/":
                    dir = dir[len(root):]

            mount = Mount(device, dir, type, opts)
            self.mounts.append(mount)

    def save(self, path):
        fh = file(path, "w")
        for mount in self.mounts:
            print >> fh, " ".join([mount.device, mount.dir, mount.type, mount.opts])
        fh.close()

    def exists(self, dir):
        """Returns True if dir exists in mounts"""
        for mount in self.mounts:
            if mount.dir.rstrip("/") == dir.rstrip("/"):
                return True
        return False
    
    def mount(self, root=None):
        for mount in self.mounts:
            mount.mount(root)

    def umount(self, root=None):
        for mount in self.mounts:
            mount.umount(root)
