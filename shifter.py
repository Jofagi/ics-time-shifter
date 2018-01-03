#!/usr/local/bin/python3
# encoding: utf-8
"""
shifter -- shifts time of events

shifter is a utilty for shifting the time of events in an iCalendar ICS file

@author:     Jofagi

@copyright:  2014 Jofagi. All rights reserved.

@license:    MIT

@contact:    github.com/Jofagi
"""

import sys
import os
import re
import datetime
import copy

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 1.0
__date__ = '2014-03-20'
__updated__ = '2014-03-20'

DEBUG = 0
TESTRUN = 0
PROFILE = 0


def verbose():
    return 0 < verbosityLevel


def very_verbose():
    return 1 < verbosityLevel


def extremely_verbose():
    return 2 < verbosityLevel


class CLIError(Exception):
    """Generic exception to raise and log different fatal errors."""

    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg

    def __str__(self):
        return self.msg

    def __unicode__(self):
        return self.msg


class IcsData:
    """Generic list of keys and values"""

    def __init__(self, lines):

        separator = re.compile(":")
        self._values = []  # must be a list so the insert order is not changed

        for l in lines:
            kv = re.split(separator, l, maxsplit=1)
            if len(kv) == 2:
                self._values.append(kv)

                if extremely_verbose():
                    print(kv[0], "=", kv[1])

            elif 0 < verbose:
                print("line not in key:value format:", l)

    def content(self):
        lines = []
        for entry in self._values:
            lines.append(entry[0] + ":" + entry[1])
        return lines


class Event(IcsData):
    """Calendar Event"""

    _START = "DTSTART"
    _END = "DTEND"
    _SUMMARY = "SUMMARY"

    def name(self):
        return self._value(self._SUMMARY)

    def _value(self, needle):
        for k, v in self._values:
            if needle == k:
                return v

    def _index(self, needle):
        idx = 0
        for kv in self._values:
            if needle == kv[0]:
                break
            idx += 1
        return idx

    def _set_start(self, new_value=""):
        self._values[self._index(self._START)][1] = new_value

    def _start(self):
        return self._value(self._START)

    def _set_end(self, new_value=""):
        self._values[self._index(self._END)][1] = new_value

    def _end(self):
        return self._value(self._END)

    def apply_delta(self, delta):
        """Applies delta hours to start and end timestamps"""

        # todo: add support for other formats
        utc_time_format = "%Y%m%dT%H%M%SZ"

        try:
            old_start = self._start()
            timestamp = datetime.datetime.strptime(old_start, utc_time_format)
            self._set_start((timestamp + delta).strftime(utc_time_format))

            old_end = self._end()
            timestamp = datetime.datetime.strptime(old_end, utc_time_format)
            self._set_end((timestamp + delta).strftime(utc_time_format))

            if very_verbose():
                print("Start:", old_start, "->", self._start())
                print("End:", old_end, "->", self._end())

            return True

        except KeyError as e:
            print("Event has no such key:", e)
            if verbose():
                print(self.content())

        except ValueError as e:
            print("Date/Time conversion error:", e)
            if verbose():
                print(self.content())

        return False


def main():
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by Jofagi on %s.
  Copyright 2014 Jofagi. All rights reserved.

  Licensed under the MIT License
  http://opensource.org/licenses/MIT

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license,
                                formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-v", "--verbose", dest="verbose",
                            action="count",
                            help="set verbosity level [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version',
                            version=program_version_message)
        parser.add_argument("-d", "--delta", dest="delta", type=int,
                            help="hours to shift by", required=True)
        parser.add_argument(dest="inPath", metavar="path",
                            help="file path [default: %(default)s]")
        parser.add_argument("-o", "--output", dest="outPath",
                            help="output file", required=True, type=str)
        parser.add_argument("-f", "--force-overwrite", dest="overwrite",
                            help="overwrite output file if it exists",
                            type=bool)

        # Process arguments
        args = parser.parse_args()

        in_path = args.inPath
        out_path = args.outPath
        overwrite = (args.overwrite or False)
        delta = (args.delta or 0)

        global verbosityLevel
        verbosityLevel = (args.verbose or 0)  # NoneType if no -v specified

        if verbose():
            print("Verbosity level:", verbosityLevel)
            print("Input:", in_path)
            print("Output:", out_path)
            print("Overwrite output:", overwrite)
            print("Delta:", delta, "hour(s)")

        if os.path.exists(out_path):
            if overwrite and verbose():
                print("overwriting existing output file", out_path)
            elif not overwrite:
                print("output file exists already!")
                return 1

        items = read_items(open(in_path))
        shifted = apply_delta(items, delta)
        write_items(shifted, open(out_path, 'w'))
        return 0

    except KeyboardInterrupt:
        # handle keyboard interrupt #
        return 0


def read_items(file):
    """Creates Event objects from input"""

    items = []  # stores events and other items
    event_count = 0

    event_begin = re.compile("BEGIN:VEVENT")
    event_end = re.compile("END:VEVENT")

    item_lines = []
    inside_event = False

    # Everything that's not an event is just treated as some generic data.
    # This is necessary for writing the "unimportant" data to the output file.      

    for line in file:

        line = line.rstrip("\r\n")

        if not inside_event and re.match(event_begin, line):
            inside_event = True

            # treat collected lines as generic data item 
            if item_lines:
                items.append(IcsData(item_lines))
                if extremely_verbose():
                    print("stored", len(item_lines), "lines of non-event data")
                item_lines.clear()

            item_lines.append(line)  # BEGIN line is part of event

        elif inside_event and re.match(event_end, line):
            inside_event = False

            # treat collected lines as event item
            item_lines.append(line)  # END line is part of event
            items.append(Event(item_lines))
            event_count = event_count + 1

            if extremely_verbose():
                print("found END of event:", len(item_lines), "lines of content")

            item_lines.clear()

        else:
            item_lines.append(line)  # Just collect line for current item

    if item_lines:
        items.append(IcsData(item_lines))
        if extremely_verbose():
            print("stored", len(item_lines), "lines of non-event data at end")

    if very_verbose():
        print("found", len(items), "total items of which", event_count,
              "are events")
    elif verbose():
        print("found", event_count, "events")

    return items


def apply_delta(items, delta_hours):
    shifted_items = []

    delta = datetime.timedelta(hours=delta_hours)

    for i in items:
        try:
            s = copy.deepcopy(i)
            if s.apply_delta(delta):
                shifted_items.append(s)
            else:
                shifted_items.append(i)  # Insert unmodified object

                if very_verbose():
                    print("event not shifted:", i.content())
                elif verbose():
                    print("event not shifted")

        except AttributeError:
            # Item is not an event object and apply_delta() does not exist
            # -- this is normal
            shifted_items.append(i)

    return shifted_items


def write_items(items, file):
    for i in items:
        for line in i.content():
            file.write(line + '\n')


if __name__ == "__main__":
    if DEBUG:
        # sys.argv.append("-h")
        sys.argv.append("-vvv")
        sys.argv.append("-d -12")
        sys.argv.append("sample.ics")
        sys.argv.append("-o sample_shifted.ics")
    if TESTRUN:
        import doctest

        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats

        profile_filename = 'shifter_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())
