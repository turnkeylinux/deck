from os.path import *

import os
import md5
import time
import errno
import shutil

from paths import Paths

import aufs
import mounts
import anoncache

from mounts import Mounts

from utils import makedirs, make_relative

deckcache = anoncache.AnonCache("/etc/deck/mounts")

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
                       ['mounts',
                        'stacks',
                        'levels',
                        'levels.refs'])

class DeckStorage(object):
    """This class takes care of a deck's representation on the filesystem."""
    class Mounts(object):
        def __get__(self, obj, type):
            if obj is None:
                return None

            path = join(obj.paths.mounts, obj.name)
            try:
                return file(path).read().rstrip()
            except:
                return None
            
        def __set__(self, obj, val):
            if not exists(obj.paths.mounts):
                makedirs(obj.paths.mounts)

            path = join(obj.paths.mounts, obj.name)
            if val is None:
                if exists(path):
                    os.remove(path)
            else:
                file(path, "w").write(val + "\n")

    mounts = Mounts()
    
    def __init__(self, deck_path):
        self.name = basename(deck_path.rstrip('/'))
        self.paths = DeckPaths(deck_path)
        self.stack_path = join(self.paths.stacks, self.name)

    def _new_level_id(self):
        """calculates a guaranteed unique new level_id"""
        def digest(s):
            return md5.md5(s).hexdigest()
        
        level_id = digest(self.name + `time.time()`)
        while exists(join(self.paths.levels, level_id)):
            level_id = digest(level_id)

        return level_id

    def add_level(self, level_id=None):
        if level_id is None:
            level_id = self._new_level_id()
        
        level_path = join(self.paths.levels, level_id)
        level_ref_path = join(self.paths.levels_refs, level_id)

        makedirs(level_path)
        makedirs(level_ref_path)

        # link the new level into the next position on the deck's stack
        stack_next_pos = max(map(int, os.listdir(self.stack_path))) + 1
        os.symlink(make_relative(self.stack_path, level_path),
                   join(self.stack_path, `stack_next_pos`))
        
        # create reference for new level pointing to this deck's stack
        os.symlink(make_relative(level_ref_path, self.stack_path),
                   join(level_ref_path, self.name))

    def exists(self):
        return exists(self.stack_path)
    
    def create(self, source_path):
        if self.exists():
            raise Error("deck `%s' already exists" % self.name)

        if not isdir(source_path):
            raise Error("source `%s' is not a directory" % source_path)

        if is_deck(source_path):
            source = Deck(source_path)
            if source.storage.paths.path != self.paths.path:
                raise Error("cannot branch a new deck from a deck in another directory")

            levels = source.storage.get_levels()
            makedirs(self.stack_path)
            os.symlink(levels[0], join(self.stack_path, "0"))
            for level in levels[1:]:
                level_id = basename(level)
                self.add_level(level_id)

            source.add_level()

            self.mounts = source.storage.mounts
        else:
            makedirs(self.stack_path)
            os.symlink(realpath(source_path), join(self.stack_path, "0"))

        self.add_level()
        
    def delete(self):
        symlinks = os.listdir(self.stack_path)
        symlinks.sort()

        # dereference the linked levels
        for symlink in symlinks[1:]:
            level_id = basename(os.readlink(join(self.stack_path, symlink)))
            
            level_path = join(self.paths.levels, level_id)
            level_ref_path = join(self.paths.levels_refs, level_id)

            # purge levels that have no more references
            os.remove(join(level_ref_path, self.name))
            if len(os.listdir(level_ref_path)) == 0:
                os.rmdir(level_ref_path)
                shutil.rmtree(level_path)

        shutil.rmtree(self.stack_path)

        # if .deck isn't handling storage for any more decks, delete it
        if not os.listdir(self.paths.stacks):
            shutil.rmtree(self.paths.path)

    def get_levels(self):
        symlinks = os.listdir(self.stack_path)
        symlinks.sort()
        
        levels = []
        for symlink in symlinks:
            source = os.readlink(join(self.stack_path, symlink))
            if not source.startswith("/"):
                source = realpath(join(self.stack_path, source))
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

        makedirs(deck_path)
        mounts = Mounts("/etc/mtab", realpath(source_path))
        if len(mounts):
            id = deckcache.new_id()
            deckcache.blob(id, "w").write(str(mounts))
            
            storage.mounts = id

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
        if self.storage.mounts:
            Mounts(deckcache.blob(self.storage.mounts)).mount(self.path)
        
    def umount(self):
        if not self.is_mounted():
            raise Error("`%s' not mounted" % self.path)

        if self.storage.mounts:
            Mounts(deckcache.blob(self.storage.mounts)).umount(self.path)
            
        aufs.umount(self.path)

    def add_level(self):
        self.storage.add_level()
        if self.is_mounted():
            beforelast, last = self.storage.get_levels()[-2:]
            operations = ("mod:%s=ro" % beforelast,
                          "prepend:%s=rw" % last)
            aufs.remount(operations, self.path)
        
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


