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
from datetime import datetime, timedelta, time, date
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


def apply_shift(start: datetime, end: datetime, delta: timedelta or None, abs_start: int or None) -> (
        datetime, datetime):

    if delta:
        pass  # nothing to be done

    elif abs_start:
        # delta must be calculated
        same_day_start = start.replace(hour=abs(abs_start), minute=0, second=0, microsecond=0)
        is_start_before_same_day_start = (start - same_day_start).total_seconds() <= 0
        shift_earlier = abs_start < 0

        if shift_earlier:
            if is_start_before_same_day_start:
                prev_day_start = same_day_start - timedelta(days=1)
                delta = prev_day_start - start
            else:
                delta = same_day_start - start

        else:  # shift to later point in time
            if is_start_before_same_day_start:
                delta = same_day_start - start
            else:
                next_day_start = same_day_start + timedelta(days=1)
                delta = start - next_day_start

    else:
        return None  # should not happen

    return start + delta, end + delta


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
                            help="hours to shift by; -1=1h earlier, 1h=1h later")
        parser.add_argument("-s", "--starttime", dest="abs_start", type=int,
                            help="hour of day to shift to: -18: shifts an event from 20:00 to 18:00 of same day; 18 "
                                 "shifts an event from 20:00 to 18:00 of next day")
        parser.add_argument(dest="in_path", metavar="path",
                            help="file path [default: %(default)s]")
        parser.add_argument("-o", "--output", dest="out_path",
                            help="output file", required=True, type=str)

        # Process arguments
        args = parser.parse_args()

        in_path = args.in_path
        out_path = args.out_path
        delta = datetime.timedelta(hours=args.delta) if args.delta else None
        abs_start = args.abs_start

        if not delta and not abs_start:
            print("Error: Either delta or starttime must be specified.")
            return 1
        elif delta and abs_start:
            print("Error: delta and starttime cannot both be specified at the same time.")
            return 1

        global verbosityLevel
        verbosityLevel = (args.verbose or 0)  # NoneType if no -v specified

        if verbose():
            print("Verbosity Level:", verbosityLevel)
            print("Input:", in_path)
            print("Output:", out_path)
            if delta:
                print("Delta:", delta.total_seconds() / 3600, " hour(s)")
            if abs_start:
                print("Start time: {0}:00".format(abs_start))

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

                    shifted_start, shifted_end = apply_shift(start, end, delta, abs_start)

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
