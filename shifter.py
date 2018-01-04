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
import datetime
from icalendar import Calendar, vDatetime

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 1.0
__date__ = '2017-01-04'
__updated__ = '2017-01-04'


def verbose():
    return 0 < verbosityLevel


def very_verbose():
    return 1 < verbosityLevel


def extremely_verbose():
    return 2 < verbosityLevel


def col_print(key: str, value: str):
    print("{0:15}: {1}".format(key, value))


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

        # Process arguments
        args = parser.parse_args()

        in_path = args.inPath
        out_path = args.outPath
        delta = datetime.timedelta(hours=args.delta or 0)

        global verbosityLevel
        verbosityLevel = (args.verbose or 0)  # NoneType if no -v specified

        if verbose():
            print("Verbosity Level:", verbosityLevel)
            print("Input:", in_path)
            print("Output:", out_path)
            print("Delta:", delta.seconds / 3600, " hour(s)")

        if os.path.exists(out_path):
            if verbose():
                print("Warning: overwriting existing output file", out_path)

        with open(in_path, 'rb') as src_file:
            cal = Calendar.from_ical(src_file.read())
            for component in cal.walk():
                if extremely_verbose():
                    col_print("component", component.name)

                if component.name == "VEVENT":
                    if verbose():
                        b = component.decoded('summary')  # decode as bytes
                        col_print("summary", b.decode())

                    # decode as datetime objects and add delta
                    start = component.decoded('dtstart')
                    end = component.decoded('dtend')

                    if extremely_verbose():
                        col_print("original start", start)
                        col_print("original end", end)

                    shifted_start = start + delta
                    shifted_end = end + delta

                    if very_verbose():
                        col_print("new start", shifted_start)
                        col_print("new end", shifted_end)

                    # delete old subcomponents so adding won't result in two subcomponents of the same kind
                    del (component['dtstart'])
                    del (component['dtend'])

                    # explicitly create vDateTime to get proper ical representation
                    component.add('dtstart', vDatetime(shifted_start))
                    component.add('dtend', vDatetime(shifted_end))

            with open(out_path, 'wb') as dst_file:
                dst_file.write(cal.to_ical())

        return 0

    except KeyboardInterrupt:
        # handle keyboard interrupt #
        return 0


if __name__ == "__main__":
    sys.exit(main())
