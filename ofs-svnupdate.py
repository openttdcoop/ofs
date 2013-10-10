#!/usr/bin/env python2

###
# This file is part of Ottd File scripts (OFS).
#
# OFS is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# OFS is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.
#
# See the GNU General Public License for more details. You should have received
# a copy of the GNU General Public License along with OFS. If not, see
# <http://www.gnu.org/licenses/>.
###



# the svn-branch you wish to update to. This should not be changed from the currently installed branch
# valid values: 'nightlies/trunk', 'stable' and 'testing' (same as stable, but also includes rc's)
branch = 'nightlies/trunk'
# directory where you keep the svn checkout. The script will run svn with this directory as working dir
sourcedir = '../'



# -------------------- DO NOT EDIT ANYTHING BELOW THIS LINE --------------------

import re
from subprocess import Popen, PIPE, CalledProcessError
from sys import exit
import os, os.path
from urllib2 import urlopen

def main():
    ReturnValues = assignReturnValues()
    # set current working directory to wherever ofs-svnupdate is located in case of relative paths
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    if branch == 'stable' or branch == 'testing':
        svnCommand = 'svn switch svn://svn.openttd.org/tags/'
    elif branch == 'nightlies/trunk':
        svnCommand = 'svn update -'
    else:
        print 'Error: Invalid branch: "%s". Please use stable, testing or nightlies/trunk ' % branch
        exit(ReturnValues.get('FAILINVALIDBRANCH'))

    newRevision = getLatestVersion(branch)
    svnCommand += newRevision
    if not os.path.isdir(sourcedir):
        exit(ReturnValues.get('FAILNOSOURCEDIR'))

    # we'll want to work from sourcedir from here on out
    os.chdir(sourcedir)

    if not execute(svnCommand, shell = True)
        exit(ReturnValues.get('FAILUPDATEERROR'))

    if not execute('make bundle', shell = True)
        exit(ReturnValues.get('FAILUPDATEERROR'))

    print 'Successfully updated OpenTTD to %s' % newRevision
    exit(ReturnValues.get('SUCCESS'))

def execute(command, shell = False):
    success = True
    print 'Executing: "%s"' % command
    if not shell:
        command = command.split()
    try:
        commandObject = Popen(command, shell=shell, stdout = PIPE)
    except OSError as e:
        print 'Error: Could not execute. Please check %s is installed and working' % command.split()[0]
        return False
    output = commandObject.stdout.read()
    commandObject.stdout.close()
    commandObject.wait()
    if commandObject.returncode:
        print 'Error: %s exited with status %s\n%s output:\n%s' % (command.split()[0], commandObject.returncode, command.split()[0], output)
        return False
    else:
        return output

def getLatestVersion(branch):
    url = 'http://finger.openttd.org/versions.txt'
    finger = urlopen(url)
    versions = {}
    for line in finger:
        versions[line.split()[-1]] = line.split()[0]
    revision = versions.get(branch)
    if revision.startswith('<'):
        actualBranch = re.sub('[<>]', '', revision)
        revision = versions.get(actualBranch)
    return revision

def assignReturnValues():
    values = {
        'SUCCESS'           : 0x00, # OpenTTD started successfully, pid written to openttd.pid
        'FAILNOSOURCEDIR'   : 0x02, # Source directory does not exist
        'FAILINVALIDBRANCH' : 0x03, # Config file contains an invalid branch
        'FAILUPDATEERROR'   : 0x04, # SVN or make failed to run successfully
    }
    return values

if __name__ == '__main__':
    main()
