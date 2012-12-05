#!/usr/bin/python
# Copyright (c) TurnKey Linux - http://www.turnkeylinux.org
#
# This file is part of Deck
#
# Deck is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.

"""Deck a filesystem

Options:
  -m            	mounts deck (the default)
  -u            	unmount deck (also refresh's the deck's fstab)
  -r            	refresh the deck's fstab (without unmounting)
  -D            	delete the deck

  --get-fstab           print fstab of deck
  --get-level=INDEX	print path of deck level
                        INDEX := <integer> | first | last

  --isdeck     	        test if path is a deck
  --isdirty  	        test if deck is dirty
  --ismounted           test if deck is mounted
"""
import sys
import help
import getopt

import deck

@help.usage(__doc__)
def usage():
    print >> sys.stderr, "Syntax: %s /path/to/dir/or/deck /path/to/new/deck" % sys.argv[0]
    print >> sys.stderr, "Syntax: %s [ -options ] /path/to/existing/deck" % sys.argv[0]

def fatal(s):
    print >> sys.stderr, "fatal: " + str(s)
    sys.exit(1)

class RigidVal:
    class AlreadySetError(Exception):
        pass
    
    def __init__(self):
        self.val = None

    def set(self, val):
        if self.val is not None:
            raise self.AlreadySetError()
        self.val = val

    def get(self):
        return self.val

def print_level(path, level):
    try:
        print deck.Deck(path).storage.get_levels()[level]
    except IndexError:
        fatal("illegal deck level (%d)" % level)

def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], 'murD',
                                       ['isdirty', 'isdeck', 'ismounted', 'get-fstab', 'get-level='])
    except getopt.GetoptError, e:
        usage(e)

    opt_get_level = None
    rigid = RigidVal()
    try:
        for opt, val in opts:
            if opt == '-h':
                usage()
            elif opt == '-m':
                rigid.set(deck.mount)
            elif opt == '-u':
                rigid.set(deck.umount)
            elif opt == '-D':
                rigid.set(deck.delete)
            elif opt == '-r':
                rigid.set(deck.refresh_fstab)
            elif opt == '--isdeck':
                rigid.set(deck.is_deck)
            elif opt == '--isdirty':
                rigid.set(deck.is_dirty)
            elif opt == '--ismounted':
                rigid.set(deck.is_mounted)
            elif opt == '--get-fstab':
                rigid.set(deck.get_fstab)
            elif opt == '--get-level':
                if val == 'first':
                    opt_get_level = 0
                elif val == 'last':
                    opt_get_level = -1
                else:
                    opt_get_level = int(val)
            
    except rigid.AlreadySetError:
        fatal("conflicting deck options")

    if not args:
        usage()
        
    func = rigid.get()
    if func is None:
        if len(args) == 2:
            func = deck.create
            
        elif len(args) == 1:
            func = deck.mount

    if func is not deck.create and len(args) != 1:
        usage("bad number of arguments")

    try:
        path = args[0]
        if opt_get_level is not None:
            print_level(path, opt_get_level)
        elif func in (deck.is_deck, deck.is_dirty, deck.is_mounted):
            error = func(path) != True
            sys.exit(error)
        elif func is deck.get_fstab:
            print deck.get_fstab(path)
        elif func is deck.create:
            source_path, new_deck = args
            func(source_path, new_deck)
        else:
            existing_deck = args[0]
            func(existing_deck)
    except deck.Error, e:
        fatal(e)
    
if __name__=="__main__":
    main()

