#!/usr/bin/python
"""Deck a filesystem

Options:
  -m            mounts deck (the default)
  -u            unmount deck
  -d            delete the deck
  -r            refresh the deck's fstab

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
    class Error(Exception):
        pass
    
    def __init__(self):
        self.val = None

    def set(self, val):
        if self.val is not None:
            raise self.Error("value already set")
        self.val = val

    def get(self):
        return self.val

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'mudr')
    except getopt.GetoptError, e:
        usage(e)

    rigid = RigidVal()
    try:
        for opt, val in opts:
            if opt == '-h':
                usage()
            elif opt == '-m':
                rigid.set(deck.mount)
            elif opt == '-u':
                rigid.set(deck.umount)
            elif opt == '-d':
                rigid.set(deck.delete)
            elif opt == '-r':
                rigid.set(deck.refresh_fstab)
    except rigid.Error:
        fatal("conflicting deck options")

    func = rigid.get()
    if func is None:
        if len(args) == 2:
            func = deck.create
            
        elif len(args) == 1:
            func = deck.mount

    if func is not deck.create and len(args) != 1:
        usage("bad number of arguments")

    if func is deck.create:
        source_path, new_deck = args
        func(source_path, new_deck)
    else:
        existing_deck = args[0]
        func(existing_deck)
    
if __name__=="__main__":
    main()

