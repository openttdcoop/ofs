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

import ConfigParser
import re
from subprocess import check_output, CalledProcessError
import sys
import optparse
import os
import os.path
import urllib2

def main():
    ReturnValues = assignReturnValues()
    # set current working directory to wherever ofs-svnupdate is located
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    oParser = optparse.OptionParser(usage='Usage: %prog [options] [server-id]')
    oParser.add_option('-C', '--config',
        help = 'specify alternate configuration file',
        dest = 'configfile', default = None, metavar = 'CONFIGFILE', type = 'string')
    options, args = oParser.parse_args()

    if options.configfile:
        configfile = options.configfile
    else:
        configfile = 'ofs.conf'
    if not os.path.isfile(configfile):
        print ('Couldn\'t read configuration from %s. Please make sure it exists or supply a different file'
            % os.path.join(os.getcwd(), configfile))
        sys.exit(ReturnValues.get('INVALIDCONFIG'))
    config = ConfigParser.ConfigParser()
    config.read(configfile)

    serverID = 'default'
    if len(args) >= 1 and args[0] in config.sections():
        serverID = args[0]

    sourcedir = config.get(serverID, 'sourcedir')
    if not os.path.isdir(sourcedir):
        print 'Sourcedir "%s" is invalid. Please modify %s' % (sourcedir, configfile)
        sys.exit(ReturnValues.get('FAILNOSOURCEDIR'))
    branch = config.get(serverID, 'branch')
    if branch == 'stable' or branch == 'testing':
        svnCommand = 'svn switch svn://svn.openttd.org/tags/'
    elif branch == 'nightlies/trunk':
        svnCommand = 'svn update -'
    else:
        print 'Invalid branch: "%s". Please use stable, testing or nightlies/trunk ' % branch
        sys.exit(ReturnValues.get('FAILINVALIDBRANCH'))

    newRevision = getLatestVersion(branch)
    svnCommand += newRevision

    # we'll want to work from sourcedir from here on out
    os.chdir(sourcedir)
    print 'Executing: "%s"' % svnCommand
    try:
        output = check_output(svnCommand, shell=True)
    except OSError as e:
        print 'Could not execute. Please check subversion is installed and working'
        sys.exit(ReturnValues.get('FAILUPDATEERROR'))
    except CalledProcessError as e:
        print 'Subversion exited with status %s\nSVN output:\n%s' % (e.returncode, e.output)
        sys.exit(ReturnValues.get('FAILUPDATEERROR'))

    command = 'make bundle'
    print 'Executing: "%s"' % command
    try:
        output = check_output(command, shell=True)
    except OSError as e:
        print 'Could not execute. Please check make is installed and working'
        sys.exit(ReturnValues.get('FAILUPDATEERROR'))
    except CalledProcessError as e:
        print 'Make exited with status %s\nMake output:\n%s' % (e.returncode, e.output)
        sys.exit(ReturnValues.get('FAILUPDATEERROR'))
    print 'Successfully updated OpenTTD to %s' % newRevision
    sys.exit(ReturnValues.get('SUCCESS'))

def getLatestVersion(branch):
    url = 'http://finger.openttd.org/versions.txt'
    finger = urllib2.urlopen(url)
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
        'INVALIDCONFIG'     : 0x01, # Program could not read from configuration file.
        'FAILNOSOURCEDIR'   : 0x02, # Source directory does not exist
        'FAILINVALIDBRANCH' : 0x03, # Config file contains an invalid branch
        'FAILUPDATEERROR'   : 0x04, # SVN or make failed to run successfully
    }
    return values

if __name__ == '__main__':
    main()
