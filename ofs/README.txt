Openttd File Scripts is just that, a collection of scripts to make
updating/starting and downloading savegames a bit easier. 
This collection is released under the GPL, a copy of which can be found in
COPYING.txt

web: http://dev.openttdcoop.org/projects/ofs/
IRC: I can usually be found in #openttd on OFTC

Installation & configuration:
 Simply put the ofs-*.py files into a directory. Once you've done that, open
 each file with a text-editor and configure the variables at the top. Read the
 comments to see what each one does. If you put them all into the same directory
 as the OpenTTD executable, you will find that most settings need not be touched.

Use cases:
 * Any time you need to do any of these operations from a remote machine. These
   commands are suitable for use in an 'ssh user@host /path/to/ofs-getsave.py url'
   style command.
 * The Soap plugin for supybot also makes use of these scripts for the functions
   they provide, wether the server is local or remote. As such they need to be
   installed on every server you manage with Soap