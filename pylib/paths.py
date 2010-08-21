import re
import os

class Paths:
    def __init__(self, path, files=[]):
        self.path = path
        self.files = {}
        for file in files:
            self.register(file)

    def __getattr__(self, name):
        if self.files.has_key(name):
            return os.path.join(self.path, self.files[name])

        raise AttributeError("no such attribute: " + name)

    def listdir(self):
        "Return a list containing the names of the entries in directory"""
        return self.files.values()

    def register(self, filename):
        attrname = re.sub(r'[\.-]', '_', filename)
        self.files[attrname] = filename

    def __str__(self):
        return self.path

    def __repr__(self):
        return "Paths('%s')" % self.path
