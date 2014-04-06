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


def verbose():
    return 0 < verbosityLevel
def veryVerbose():
    return 1 < verbosityLevel
def extremelyVerbose():
    return 2 < verbosityLevel

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

class IcsData:
    '''Generic list of keys and values''' 
    def __init__(self, lines):
        
        separator = re.compile(":")
        self._values = {}
        
        for l in lines:
            kv = re.split(separator, l, maxsplit=1)
            if len(kv) == 2:
                self._values[kv[0]] = kv[1]
                
                if extremelyVerbose():
                    print(kv[0],"=", kv[1])
                    
            elif 0 < verbose:
                print("line not in key:value format:", l)

    def content(self):
        lines = []
        for k, v in self._values.items():
            lines.append(k + ":" + v)
        return lines
            

class Event (IcsData):
    '''Calendar Event'''
        
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
        
        global verbosityLevel
        verbosityLevel = (args.verbose or 0) # NoneType if no -v specified
        

        if verbose():
            print("Verbosity level:", verbosityLevel)
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

def readItems(file):
    '''Creates Event objects from input'''
    
    items = [] # stores events and other items
    eventCount = 0
    
    eventBegin = re.compile("BEGIN:VEVENT")
    eventEnd = re.compile("END:VEVENT")
    
    itemLines = []
    insideEvent = False
    
    # Everything that's not an event is just treated as some generic data.
    # This is necessary for writing the "unimportant" data to the output file.      
    
    for line in file:        
        
        if not insideEvent and re.match(eventBegin, line):
            insideEvent = True
            
            # treat collected lines as generic data item 
            if 0 < len(itemLines):
                items.append(IcsData(itemLines))
                itemLines.clear()

            itemLines.append(line) # BEGIN line is part of event
        
        elif insideEvent and re.match(eventEnd, line):
            insideEvent = False
            
            # treat collected lines as event item
            itemLines.append(line) # END line is part of event
            items.append(Event(itemLines))
            eventCount = eventCount + 1
            
            if extremelyVerbose():
                print("found END of event:", len(itemLines), "lines of content")
            
            itemLines.clear()
        
        else:
            itemLines.append(line) # Just collect line for current item
            

    if verbose():
        print("found", eventCount, "events")
    elif veryVerbose():
        print("found", len(items), "total items of which", eventCount, "are events")

    return items

def applyDelta(items, delta):
    shiftedItems = []
    
    for i in items:
        try:
            startTime = i.start()
            endTime = i.end()
            
        except AttributeError:
            pass # Item is not an event object - this is normal
        except KeyError as e:
            # It's and event but has no such key - this is bad
            print("Event has no such key:", e);
            if verbose():
                print(i.content());
    
    return shiftedItems
 
                
def shift(path, delta):
    try:
        items = readItems(open(path))
        items = applyDelta(items, delta)
                    
    except OSError as e:
        print(e)
        return 1
        
    return 0
    

if __name__ == "__main__":
    if DEBUG:
        #sys.argv.append("-h")
        sys.argv.append("-vvv")
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