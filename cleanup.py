#!/usr/bin/env python

import os
import re
import sys
import getopt
import logging as l

from dirscan  import *
from datetime import *
from os.path  import *
from stat     import *

args   = None
debug  = False
status = False
opts   = { 'dryrun': False, 'ages': False }

if len(sys.argv) > 1:
    options, args = getopt(sys.argv[1:], 'nvuA', {})

    for o, a in options:
        if o in ('-v'):
            debug = True
            l.basicConfig(level = l.DEBUG,
                          format = '[%(levelname)s] %(message)s')
        elif o in ('-u'):
            status = True
            l.basicConfig(level = l.INFO, format = '%(message)s')
        elif o in ('-n'):
            opts['dryrun'] = True
        elif o in ('-A'):
            opts['ages'] = True

if not args or "trash" in args:
    DirScanner(directory        = expanduser('~/.Trash'),
               days             = 14,
               cacheAttrs       = True,
               maxSize          = '1%',
               sudo             = True,
               depth            = 0,
               minimalScan      = True,
               onEntryPastLimit = safeRemove,
               **opts).scanEntries()

    if isdir('/.Trashes/501'):
        DirScanner(directory        = '/.Trashes/501',
                   days             = 7,
                   cacheAttrs       = True,
                   maxSize          = '1%',
                   sudo             = True,
                   depth            = 0,
                   minimalScan      = True,
                   onEntryPastLimit = safeRemove,
                   **opts).scanEntries()

    for name in os.listdir("/Volumes"):
        path = join("/Volumes", name, ".Trashes", "501")
        if exists(path):
            DirScanner(directory        = path,
                       days             = 14,
                       cacheAttrs       = True,
                       maxSize          = '2%',
                       sudo             = True,
                       depth            = 0,
                       minimalScan      = True,
                       onEntryPastLimit = safeRemove,
                       **opts).scanEntries()

if not args or "backups" in args:
    DirScanner(directory        = expanduser('~/.emacs.d/backups'),
               days             = 28,
               mtime            = True,
               sudo             = True,
               depth            = 0,
               maxSize          = '1%',
               minimalScan      = True,
               onEntryPastLimit = safeRemove,
               **opts).scanEntries()

    for name in os.listdir("/Volumes"):
        path = join("/Volumes", name, ".backups")
        if exists(path):
            DirScanner(directory        = path,
                       days             = 28,
                       mtime            = True,
                       sudo             = True,
                       depth            = 0,
                       maxSize          = '1%',
                       minimalScan      = True,
                       onEntryPastLimit = safeRemove,
                       **opts).scanEntries()
