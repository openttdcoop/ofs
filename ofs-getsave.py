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
import sys
import optparse
import os
import os.path
import urllib2

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

    if len(args) < 1:
        print 'Error: No URL supplied.'
        sys.exit(ReturnValues.get('BADURL'))
    serverID = 'default'
    if len(args) > 1:
        if args[0] in config.sections():
            serverID = args[0]
        saveUrl = args[1]
    else:
        saveUrl = args[0]

    savedir = config.get(serverID, 'savedir')
    if not os.path.isdir(savedir):
        print 'Savedir "%s" is invalid. Please modify %s' % (savedir, configfile)
        sys.exit(ReturnValues.get('INVALIDSAVEDIR'))

    savegame = downloadFile(saveUrl, savedir)
    if isinstance(savegame, tuple):
        print 'Encountered error %s while downloading %s. File not saved' % (savegame[0], savegame[1])
        sys.exit(ReturnValues.get('BADURL'))
    elif not os.path.isfile(savegame):
        print 'File downloaded succesfully, but file was not written. Please check your permissions on %s' % savedir
        sys.exit(ReturnValues.get('DOWNLOADFAILED'))
    print 'File downloaded succesfully. File saved as %s' % savegame
    sys.exit(ReturnValues.get('SUCCESS'))

def downloadFile(url, directory):
    try:
        savefile = os.path.join(directory, os.path.basename(url))
        f = urllib2.urlopen(url)
        with open(savefile, "wb") as local_file:
            local_file.write(f.read())
    except urllib2.HTTPError, e:
        return (e.code, url)
    except urllib2.URLError, e:
        return (e.reason, url)
    except IOError:
        return 'couldn\'t write file'
    return savefile

def assignReturnValues():
    values = {
        'SUCCESS'         : 0x00, # Program finished successfully
        'INVALIDCONFIG'   : 0x01, # Program could not read from configuration file.
        'INVALIDSAVEDIR'  : 0x02, # Savedir is not a valid or existing directory
        'DOWNLOADFAILED'  : 0x03, # Failed to write downloaded file to disk
        'BADURL'          : 0x04, # Download failed due to bad url (eg, 404, not an actual url)
    }
    return values

if __name__ == '__main__':
    main()
