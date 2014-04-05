#!/usr/local/bin/python2.7
# encoding: utf-8
'''
shifter -- shifts time of events

shifter is a utilty for shifting the time of events in an iCalendar ICS file

It defines classes_and_methods

@author:     Jofagi

@copyright:  2014 Jofagi. All rights reserved.

@license:    MIT

@contact:    github.com/Jofagi
@deffield    updated: Updated
'''

import sys
import os
import re

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2014-03-20'
__updated__ = '2014-03-20'

DEBUG = 1
TESTRUN = 0
PROFILE = 0

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

class Event:
    '''Calendar Event'''
    
    def __init__(self, lines):
        
        separator = re.compile(":")
        self._values = {}
        
        for l in lines:
            kv = re.split(separator, l, maxsplit=1)
            if len(kv) == 2:
                self._values[kv[0]] = kv[1]
                if 3 < verbose:
                    print(kv[0],"=", kv[1])
            elif 0 < verbose:
                print("line not in key:value format:", l)
                        
        
    def name(self):
        return self._values["SUMMARY"]
    
    def start(self):
        return self._values["DTSTART"]
    
    def end(self):
        return self._values["DTEND"]
    

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
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
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument(dest="path", help="file path [default: %(default)s]", metavar="path")
        parser.add_argument("-d", "--delta", dest="delta", help="hours to shift by", required=True, type=int)

        # Process arguments
        args = parser.parse_args()

        path = args.path
        delta = (args.delta or 0)
        
        global verbose
        verbose = (args.verbose or 0) # NoneType if no -v specified
        

        if 0 < verbose:
            print("Verbosity level:", verbose)
            print("Path:", path)
            print("Delta:", delta, "hour(s)")

        
        return shift(path, delta)
        
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
# This prevents pydev from printing a traceback
#    except Exception as e:
#        if DEBUG or TESTRUN:
#            raise(e)
#        indent = len(program_name) * " "
#        sys.stderr.write(program_name + ": " + repr(e) + "\n")
#        sys.stderr.write(indent + "  for help use --help")
#        return 2

def readEvents(file):
    '''Creates Event objects from input'''
    
    events = []
    
    beginPattern = re.compile("BEGIN:VEVENT")
    endPattern = re.compile("END:VEVENT")
    
    eventLines = []
    insideEvent = False
        
    for line in file:
        # Searching for and found a BEGIN? Start adding
        if not insideEvent and re.match(beginPattern, line):
            insideEvent = True
            if 2 < verbose:
                print("found event BEGINning")
            continue
        
        # Found an END while adding lines?
        # Create event and stop adding lines until the next BEGIN 
        if insideEvent and re.match(endPattern, line):
            if 2 < verbose:
                print("found END of event:", len(eventLines), "lines of content")
            events.append(Event(eventLines))
            insideEvent = False
            eventLines.clear()
            continue
        
        # Just inside an event? Add line
        if insideEvent:
            eventLines.append(line)
            if 3 < verbose:
                print("read:", line)
        elif 3 < verbose:
            print("ignore:", line)
            
    if 1 < verbose:
        print(len(events), "events found")

    return events

                
def shift(path, delta):
    try:
        events = readEvents(open(path))
                    
    except OSError as e:
        print(e)
        return 1
        
    return 0
    

if __name__ == "__main__":
    if DEBUG:
        #sys.argv.append("-h")
        sys.argv.append("-vvvv")
        sys.argv.append("-d -1")
        sys.argv.append("sample.ics")
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