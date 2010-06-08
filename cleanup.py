#!/usr/bin/env python

import os
import re
import sys
import getopt
import subprocess
import random
import logging as l

sys.path.append('/Users/johnw/src/dirscan')

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

########################################################################

window = 28

random.seed()

def verifyContents(entry):
    checksumSet = False
    if not opts['dryrun']:
        p = subprocess.Popen("xattr -p checksum-sha1 '%s'" % entry.path,
                             shell = True, stdout = subprocess.PIPE,
                             stderr = subprocess.PIPE)
        sts = os.waitpid(p.pid, 0)
        if sts[1] == 0:
            sha = p.stdout.read()[:-1]
            print "ADDED: %s (SHA1 %s)" % (entry.path, sha)
            entry._checksum = sha # we know what it should be from disk
            checksumSet = True

    if not checksumSet:
        print "ADDED:", entry.path

    entry._lastCheck = rightNow - timedelta(random.randint(0, window))

    return True

def alertAdminChanged(entry):
    print "CHANGED:", entry.path
    with open(expanduser('~/Desktop/verify.log'), "a") as fd:
        fd.write("%s - CHANGED: %s\n" % (rightNow, entry.path))
    return True

def alertAdminRemoved(entry):
    print "REMOVED:", entry.path
    with open(expanduser('~/Desktop/verify.log'), "a") as fd:
        fd.write("%s - REMOVED: %s\n" % (rightNow, entry.path))
    return True

for path in ['/Volumes/RAID/Archives',
             '/Volumes/RAID/Backups',
             '/Volumes/RAID/Media',
             '/Volumes/archive',
             '/Volumes/games',
             '/Volumes/backup',
             '/Volumes/media']:
    if isdir(path):
        DirScanner(directory         = expanduser(path),
                   check             = True,
                   checkWindow       = window,
                   ignoreFiles       = [ '^\.files\.dat$'
                                       , '^\.DS_Store$'
                                       , '^\.localized$'
                                       , '\.dtMeta$'
                                       , '\.sparsebundle$'
                                       , '^[0-9]{18}$'
                                       , '^Saves$'
                                       , '^Cache$'
                                       , '\.dxo$'
                                       ],
                   useChecksumAlways = True,
                   onEntryAdded      = verifyContents,
                   onEntryChanged    = alertAdminChanged,
                   onEntryRemoved    = alertAdminRemoved,
                   **opts).scanEntries()

# cleanup.py ends here
