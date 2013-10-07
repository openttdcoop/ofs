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
from subprocess import check_output, CalledProcessError
import sys
import optparse
import os
import os.path

def main():
    ReturnValues = assignReturnValues()
    # set current working directory to wherever ofs-getsave is located
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    oParser = optparse.OptionParser(usage='Usage: %prog [options] [server-id] savegame-url')
    oParser.add_option('-C', '--config',
        help = 'specify alternate configuration file',
        dest = 'configfile', default = None, metavar = 'CONFIGFILE', type = 'string')
    options, args = oParser.parse_args()

    if options.configfile:
        configfile = options.configfile
    else:
        configfile = 'ofs.conf'
    if not os.path.isfile(configfile):
        print 'Couldn\'t read configuration from %s. Please make sure it exists or supply a different file' % os.path.join(os.getcwd(), configfile))
        sys.exit(ReturnValues.get('INVALIDCONFIG'))
    config = ConfigParser.ConfigParser()
    config.read(configfile)

    serverID = 'default'
    if len(args) >= 1 and args[0] in config.sections():
        serverID = args[0]

    gamedir = config.get(serverID, 'gamedir')
    if not os.path.isdir(gamedir):
        sys.exit(ReturnValues.get('FAILNOGAMEDIR'))
    executable = os.path.join(gamedir, 'openttd')
    if not os.path.isfile(executable):
        sys.exit(ReturnValues.get('FAILNOEXECTUABLE'))
    pidfile = os.path.join(gamedir, 'openttd.pid')
    status = checkStatus(pidfile, executable)
    if status:
        sys.exit(ReturnValues.get('SERVERRUNNING'))
    serverconfig = os.path.join(gamedir, 'openttd.cfg')
    if not os.path.isfile(serverconfig):
        sys.exit(ReturnValues.get('FAILNOSERVERCONF'))
    autosavedir = os.path.join(config.get(serverID, 'savedir'), 'autosave/')
    lastsave = getLatestAutoSave(autosavedir)
    parameters = config.get(serverID, 'parameters')

    command = []
    command.append(executable)
    command.extend(['-D', '-f', '-c', serverconfig])
    if not lastsave == None and os.path.isfile(lastsave):
        command.extend(['-g', lastsave])
    if parameters:
        parameters = parameters.split()
        command.extend(parameters)

    commandtext = ' '.join(command)
    print 'Executing: %s' % commandtext
    try:
        output = check_output(command)
    except OSError as e:
        sys.exit(ReturnValues.get('FAILOSERROR'))
    except CalledProcessError as e:
        print 'Game did not start correctly. Exit code: %s\n Program output:\n %s' % (e.returncode, e.output)
        sys.exit(ReturnValues.get('FAILNONZEROEXIT'))

    pid = None
    for line in output.splitlines():
        print 'OpenTTD output: %s' % line
        if 'Forked to background with pid' in line:
            words = line.split()
            pid = words[6]
            try:
                with open(pidfile, 'w') as pf:
                    pf.write(str(pid))
            except NameError as e:
                print 'Couldn\'t write to pidfile: %s' % e
                sys.exit(ReturnValues.get('SUCCESSNOPIDFILE'))
            sys.exit(ReturnValues.get('SUCCESS'))
    sys.exit(ReturnValues.get('FAILNOPIDFOUND'))

def checkStatus(pidfile, executable):
    try:
        with open(pidfile) as pf:
            pid = pf.readline()
    except IOError:
        return False
    exename = os.path.basename(executable)
    try:
        output = check_output('ps -A', shell=True)
    except CalledProcessError as e:
        print 'Couldn\'t run ps -A'
        return False
    for line in output.splitlines():
        if not line == '' and not line == None:
            fields = line.split()
            pspid = fields[0]
            pspname = fields[3]
            if pspid == pid and pspname == exename:
                return True
    else:
        return False

def getLatestAutoSave(autosavedir):
    max_mtime = 0
    save = None
    for fname in os.listdir(autosavedir):
        if fname.startswith('autosave'):
            fullpath = os.path.join(autosavedir, fname)
            mtime = os.stat(fullpath).st_mtime
            if mtime > max_mtime:
                max_mtime = mtime
                save = fullpath
    return save

def assignReturnValues():
    values = {
        'SUCCESS'           : 0x00, # OpenTTD started succesfully, pid written to openttd.pid
        'INVALIDCONFIG'     : 0x01, # Program could not read from configuration file.
        'SERVERRUNNING'     : 0x02, # Game is already running, no point starting another instance
        'SUCCESSNOPIDFILE'  : 0x03, # Openttd started succesfully, but could not write to openttd.pid
        'FAILNOGAMEDIR'     : 0x04, # Gamedir is invalid or does not exist
        'FAILNOEXECTUABLE'  : 0x05, # Executable does not exist
        'FAILNOSERVERCONF'  : 0x06, # No OpenTTD configuration file found
        'FAILOSERROR'       : 0x07, # Couldn't run the command
        'FAILNONZEROEXIT'   : 0x08, # OpenTTD returned with exitcode <> 0
        'FAILNOPIDFOUND'    : 0x09, # No pid found in OpenTTD output, OpenTTD probably didn't start correctly
    }
    return values

if __name__ == '__main__':
    main()
check