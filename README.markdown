Gpxpy is a python library for working with geographic data stored in [GPX][] files. It provides a pythonic interface to the track, route, and waypoint concepts defined in the [GPX schema][schema] along with a number of utility functions for common manipulations. It does not provide any functionality around getting data to/from your GPS device. You should use [gpsbabel][] for that. It does provide a number of command line utilities similar in scope to gpsbabel with a slightly more humane interface.

[gpx]:http://www.topografix.com/gpx.asp
[gpsbabel]:http://www.gpsbabel.org/
[schema]:http://www.topografix.com/GPX/1/1/

This project is a work in progress,  it was born out of a frustration with working with the gpsbabel command line and as an introduction to Python. It has not been robustly tested or documented, but it works for me, and it may work for you too. If it doesn't, feel free to file bugs or submit patches. 

Enjoy!

# Dependencies 

Requires python 2.6 and the following additional libraries:

- [argparse][]
- [pytz][]
- [isodate][]

[argparse]:http://pypi.python.org/pypi/argparse/1.2.1
[pytz]: http://pytz.sourceforge.net/
[isodate]:http://pypi.python.org/pypi/isodate/0.4.0

# Library 

Documentation to come. 

# Scripts 

gpxinfo - summarize info about a particular gpx file

gpxmerge - reads multiple GPX files and outputs a single file. Removes duplicates. Tracks with multiple segments may be collapsed into a single segment with the -j option

gpxfilter - restrict contents of a GPX file to a specific geographic area or time period. 

gpxsplit - break apart tracks according to time or distance

# License

See LICENSE file.

# Author

Written by Joel Carranza