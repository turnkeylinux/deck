from os.path import *

import os
import md5
import time
import shutil

from paths import Paths

import aufs

class Error(Exception):
    pass

def is_deck(path):
    try:
        Deck(path)
        return True
    except Error:
        return False

class DeckPaths(Paths):
    def __init__(self, path=None):
        path = join(dirname(realpath(path)), ".deck")
        Paths.__init__(self, path,
                       ['struct',
                        'levels',
                        'levels.refs'])

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

class Deck:
    @staticmethod
    def new_level_id(levels_path, name):
        """calculates a guaranteed unique new level_id"""
        def digest(s):
            return md5.md5(s).hexdigest()
        
        level_id = digest(name + `time.time()`)
        while exists(join(levels_path, level_id)):
            level_id = digest(level_id)

        return level_id
    
    @classmethod
    def init_create(cls, source_path, deck_path):
        if not isdir(source_path):
            raise Error("source `%s' is not a directory" % source_path)

        if exists(deck_path) and \
               (not isdir(deck_path) or len(os.listdir(deck_path)) != 0):
            raise Error("`%s' exists and is not an empty directory" % deck_path)

        if is_deck(deck_path):
            raise Error("`%s' deck already created" % deck_path)

        deck_name = basename(deck_path.rstrip("/"))
        paths = DeckPaths(deck_path)
        
        level_id = cls.new_level_id(paths.levels, deck_name)
        level_id_path = join(paths.levels, level_id)
        level_id_ref_path = join(paths.levels_refs, level_id)

        deck_struct_path = join(paths.struct, deck_name)

        os.makedirs(level_id_path)
        os.makedirs(level_id_ref_path)
        os.makedirs(deck_struct_path)

        symlinks = [ realpath(source_path), make_relative(deck_struct_path, level_id_path) ]
        for i in range(len(symlinks)):
            os.symlink(symlinks[i], join(deck_struct_path, `i`))

        # increase reference count of level_id
        os.symlink(make_relative(level_id_ref_path, deck_struct_path),
                   join(level_id_ref_path, deck_name))

        os.makedirs(deck_path)
        deck = cls(deck_path)
        deck.mount()
        return deck

    @classmethod
    def delete(cls, deck_path):
        deck = cls(deck_path)
        if deck.is_mounted():
            deck.umount()
        os.rmdir(deck_path)

        shutil.rmtree(deck.struct_path)
        level_ids = ( basename(level) for level in deck.levels[1:] )
        for level_id in level_ids:

            level_path = join(deck.paths.levels, level_id)
            level_ref_path = join(deck.paths.levels_refs, level_id)

            os.remove(join(level_ref_path, deck.name))
            if len(os.listdir(level_ref_path)) == 0:
                os.rmdir(level_ref_path)
                shutil.rmtree(level_path)
        
    def __init__(self, path):
        self.path = path
        self.paths = DeckPaths(path)
        self.name = basename(path.rstrip("/"))
        self.struct_path = join(self.paths.struct, self.name)
        
        if not isdir(self.struct_path):
            raise Error("not a deck `%s'" % path)

        levels = []
        for symlink in os.listdir(self.struct_path):
            source = os.readlink(join(self.struct_path, symlink))
            if not source.startswith("/"):
                source = realpath(join(self.struct_path, source))
            levels.append(source)

        self.levels = levels

    def is_mounted(self):
        return aufs.is_mounted(self.path)

    def mount(self):
        if self.is_mounted():
            raise Error("`%s' already mounted" % self.path)

        aufs.mount(list(reversed(self.levels)), self.path)

    def umount(self):
        if not self.is_mounted():
            raise Error("`%s' not mounted" % self.path)

        aufs.umount(self.path)
        
def create(source_path, deck_path):
    Deck.init_create(source_path, deck_path)

def mount(deck_path):
    Deck(deck_path).mount()

def umount(deck_path):
    Deck(deck_path).umount()

def refresh_fstab(deck_path):
    print "refresh_fstab(%s)" % deck_path

def delete(deck_path):
    Deck.delete(deck_path)


