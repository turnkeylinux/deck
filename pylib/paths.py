"""
DESCRIPTION

High-level class for representing file paths.

File paths are accessible as instance attributes
. and - are replaced for _

The files attribute is "inherited".

USAGE

class FooPaths(Paths):
	files = ["foo", "sub.dir/sub-file"]

class BarPaths(FooPaths):
	files = [ "bar" ] + subdir("sub.dir2", ["sub-file2"])

paths = BarPaths("/tmp")
print paths.foo
print paths.sub_dir
print paths.sub_dir.sub_file
print paths.sub_dir2.sub_file2

"""
import re
import os
from os.path import *

class Paths:
    files = []
    def __init__(self, path, files=[]):
        self.path = path
        self.files = {}

        def classfiles(cls):
            files = cls.files
            for base in cls.__bases__:
                if issubclass(base, Paths):
                    files += classfiles(base)

            return files

        for file in files + classfiles(self.__class__):
            self.register(file)

    def __getattr__(self, name):
        if self.files.has_key(name):
            return join(self.path, self.files[name])

        raise AttributeError("no such attribute: " + name)

    @staticmethod
    def _fname2attr(fname):
        return re.sub(r'[\.-]', '_', fname)
    
    def listdir(self):
        "Return a list containing the names of the entries in directory"""
        return self.files.values()

    def register(self, filename):
        if '/' in filename:
            subdir, filename = filename.split('/', 1)
            attr = self._fname2attr(subdir)
            subpaths = getattr(self, attr, None)
            if not subpaths or not isinstance(subpaths, Paths):
                subpaths = Paths(join(self.path, subdir))
                setattr(self, attr, subpaths)

            subpaths.register(filename)
        else:
            attr = self._fname2attr(filename)
            self.files[attr] = filename

    def __str__(self):
        return self.path

    def __repr__(self):
        return "Paths('%s')" % self.path

def subdir(dir, files):
    return [ os.path.join(dir, file) for file in files ]

def test():
    class FooPaths(Paths):
            files = ["foo", "sub.dir/sub-file"]

    class BarPaths(FooPaths):
            files = [ "bar" ] + subdir("sub.dir2", ["sub-file2"])

    paths = BarPaths("/tmp")
    print paths.foo
    print paths.sub_dir
    print paths.sub_dir.sub_file
    print paths.sub_dir2.sub_file2

if __name__ == "__main__":
    test()

