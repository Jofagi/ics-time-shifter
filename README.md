ics-time-shifter
================

Shifts events in an ICS file by a specified time.

This was created to move the events of an ICS file, supplied by a third party,
so the default reminder of the mobile phone's calendar app could be used.
Manually modifying each event of the calendar on the phone was no longer
necessary.   


USAGE
-----
```
shifter.py [-h] [-v] [-V] -d DELTA -o OUTPATH [-f OVERWRITE] path

  path                  file path
  -h, --help            show this help message and exit
  -v, --verbose         set verbosity level
  -V, --version         show program's version number and exit
  -d DELTA, --delta DELTA
                        hours to shift by
  -o OUTPATH, --output OUTPATH
                        output file
  -f OVERWRITE, --force-overwrite OVERWRITE
                        overwrite output file if it exists
```

EXAMPLES
-------

1. shift events 12 hours backward:
    ```
    python shifter -d -12 -o events_earlier.ics events.ics
    ``` 
1. shift events 12 hours forward:
    ```
    python shifter -d 12 -o events_later.ics events.ics
    ```


COPYRIGHT
---------
  Created by Jofagi on 2014-03-20.
  Copyright 2014 Jofagi. All rights reserved.

  Licensed under the MIT License
  http://opensource.org/licenses/MIT

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.