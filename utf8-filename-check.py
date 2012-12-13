#!/usr/bin/env python
# utf8-filename-check.py - detect invalid UTF-8 in filenames
#
# Author: Roman Yepishev <roman.yepishev@gmail.com>
#
# Copyright 2010 Roman Yepishev.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Script for invalid UTF-8 detection in filenames"""

import os
import sys
from optparse import OptionParser

# Since syncdaemon breaks on the first filename, the only
# solution was to fix files sequentially.
#                                          Until now! :)

class Utf8FilenameChecker(object):
    """
    This is the application itself
    """
    def __init__(self):
        self.broken_filenames = []
        self.broken_dirnames = []
        self.encoding = None

    def set_encoding(self, encoding=None):
        self.encoding = encoding

    def assert_utf8_filename(self, filename, basename, broken_list):
        """Checks that filename is a valid utf-8 string. If it is not, then
        add that filename to corresponding broken_list"""
        filename_decoded = None
        try:
            filename_decoded = filename.decode('UTF-8')
        except UnicodeDecodeError:
            # we still need to fix the output
            basename_decoded = basename.decode('UTF-8', 'replace')
            filename_decoded = filename.decode('UTF-8', 'replace')

            path_recovered = None

            if self.encoding is not None:
                basename_recovered = basename.decode(self.encoding, 'replace')
                filename_recovered = filename.decode(self.encoding, 'replace')

                path_recovered = os.path.join(basename_recovered, \
                                              filename_recovered)

                path_recovered = path_recovered.encode('UTF-8')

            broken_item = os.path.join(basename_decoded, \
                                        filename_decoded)

            broken_item = broken_item.encode('UTF-8')

            broken_list.append([broken_item, path_recovered])

    def scan(self, path='.'):
        """Performs traversal of the directories and printing of the
        results"""
        # no need to show all the folder for every scanned folder
        self.broken_dirnames = []

        # no need to show all the files for every folder
        self.broken_filenames = []

        for root, dirs, files in os.walk(path):
            for filename in files:
                self.assert_utf8_filename(filename, root, self.broken_filenames)
            for dirname in dirs:
                self.assert_utf8_filename(dirname, root, self.broken_dirnames)

        if len(self.broken_filenames) == 0 and len(self.broken_dirnames) == 0:
            print "You don't have any filenames with broken names in %s" % (
                    path)

        if len(self.broken_dirnames) > 0:
            print 'Rename the following directories:'
            for item in self.broken_dirnames:
                candidate = item[1]
                print " {0} (candidate: {1})".format(item[0], candidate)

        print 

        if len(self.broken_filenames) > 0:
            print 'Rename the following files:'
            for item in self.broken_filenames:
                candidate = item[1]
                print " {0} (candidate: {1})".format(item[0], candidate)

if __name__ == "__main__":

    usage = "Usage: %prog [-e encoding] /path1 [ /path2 ... ]"

    parser = OptionParser(usage=usage)

    parser.add_option("-e", "--encoding", dest="encoding", \
                      help="Set encoding for filename printing")

    (options, args) = parser.parse_args(sys.argv)

    checker = Utf8FilenameChecker()
    if options.encoding:
        checker.set_encoding(options.encoding)

    if len(args) > 1:
        for arg in args[1:]:
            checker.scan(arg)
    else:
        checker.scan()
