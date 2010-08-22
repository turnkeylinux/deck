from os.path import *

import os
import md5
import time
import shutil

from paths import Paths

import aufs

class Error(Exception):
    pass

class DeckPaths(Paths):
    def __init__(self, path=None):
        path = join(dirname(realpath(path)), ".deck")
        Paths.__init__(self, path,
                       ['structs',
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

class DeckStorage:
    """This class takes care of a deck's representation on the filesystem."""
    
    def __init__(self, deck_path):
        self.name = basename(deck_path.rstrip('/'))
        self.paths = DeckPaths(deck_path)
        self.struct_path = join(self.paths.structs, self.name)

    def _new_level_id(self):
        """calculates a guaranteed unique new level_id"""
        def digest(s):
            return md5.md5(s).hexdigest()
        
        level_id = digest(self.name + `time.time()`)
        while exists(join(self.paths.levels, level_id)):
            level_id = digest(level_id)

        return level_id

    def add_level(self):
        level_id = self._new_level_id()
        
        level_path = join(self.paths.levels, level_id)
        level_ref_path = join(self.paths.levels_refs, level_id)

        os.makedirs(level_path)
        os.makedirs(level_ref_path)

        # link the new level into the next position on the deck's struct
        struct_next_pos = max(map(int, os.listdir(self.struct_path))) + 1
        os.symlink(make_relative(self.struct_path, level_path),
                   join(self.struct_path, `struct_next_pos`))
        
        # create reference for new level pointing to this deck's struct
        os.symlink(make_relative(level_ref_path, self.struct_path),
                   join(level_ref_path, self.name))

    def exists(self):
        return exists(self.struct_path)
    
    def create(self, source_path):
        if self.exists():
            raise Error("deck `%s' already exists" % self.name)

        if not isdir(source_path):
            raise Error("source `%s' is not a directory" % source_path)

        os.makedirs(self.struct_path)
        os.symlink(realpath(source_path), join(self.struct_path, "0"))

        self.add_level()
        
    def delete(self):
        symlinks = os.listdir(self.struct_path)
        symlinks.sort()

        # dereference the linked levels
        for symlink in symlinks[1:]:
            level_id = basename(os.readlink(join(self.struct_path, symlink)))
            
            level_path = join(self.paths.levels, level_id)
            level_ref_path = join(self.paths.levels_refs, level_id)

            # purge levels that have no more references
            os.remove(join(level_ref_path, self.name))
            if len(os.listdir(level_ref_path)) == 0:
                os.rmdir(level_ref_path)
                shutil.rmtree(level_path)

        shutil.rmtree(self.struct_path)

        # if .deck isn't handling storage for any more decks, delete it
        if not os.listdir(self.paths.structs):
            shutil.rmtree(self.paths.path)

    def get_levels(self):
        symlinks = os.listdir(self.struct_path)
        symlinks.sort()
        
        levels = []
        for symlink in symlinks:
            source = os.readlink(join(self.struct_path, symlink))
            if not source.startswith("/"):
                source = realpath(join(self.struct_path, source))
            levels.append(source)

        return levels

class Deck:
    """This class is the front-end of a deck"""
    @classmethod
    def init_create(cls, source_path, deck_path):
        if exists(deck_path) and \
               (not isdir(deck_path) or len(os.listdir(deck_path)) != 0):
            raise Error("`%s' exists and is not an empty directory" % deck_path)

        storage = DeckStorage(deck_path)
        storage.create(source_path)

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

        storage = DeckStorage(deck_path)
        storage.delete()
        
    def __init__(self, path):
        self.path = path
        self.storage = DeckStorage(path)
        if not self.storage.exists():
            raise Error("`%s' not a deck" % path)
        
    def is_mounted(self):
        return aufs.is_mounted(self.path)

    def mount(self):
        if self.is_mounted():
            raise Error("`%s' already mounted" % self.path)

        levels = self.storage.get_levels()
        levels.reverse()
        aufs.mount(levels, self.path)
        
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


