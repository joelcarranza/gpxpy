GPXPY - a set of tools for dealing with GPX files

Dependencies
- argparse
- timezone?
- iso lib?

Goal is produce a basic library along with a number of simple command line utilities with the goal of creating "Maps" - i.e KML files or images or whatever. GPX files are the basis of the work, use gpsbable to get whatever into GPX format if you are feeling saucy.

GPXPY

Data model for GPX files
Waypoint - location with optional time elevation components
Path - ordered list of waypts

Paths represent both tracks and routes and waypoints represent all points in model

GPxpy.py is library - if run standalone summarizes a passed in file. 

Utilities:
Filter trackpoints by time
Prune wpts/track/route by type,specific name
Prune very short tracks
Split according to time/distance
Split around specified pt 
Simplify , basic and topologically 
Produce KML file
Interpolate JMT track from partial path
Elevation chart
Location names using webservice (geocode)

Google Maps 
- no labelling, but you can produce labels by setting placemark icon to a image with drawn text, using google charts API (Dynamic Icons)
http://code.google.com/apis/chart/docs/gallery/dynamic_icons.html
Existing list of icons:
http://www.visual-case.it/cgi-bin/vc/GMapsIcons.pl
See also numbers:
http://code.google.com/p/google-maps-icons/wiki/NumericIcons
Days of the week:
http://code.google.com/p/google-maps-icons/wiki/EventsIcons

Filter/Merging/Simplification



KML Genereration
KML Reference
http://code.google.com/apis/kml/documentation/kmlreference.html#feature

General Command line utilities
process -i in.gpx -o out.gpx 
if -i or -o does not exist then read from stdin stdout
Use argparse (included in python 2.7 but can download instead) (?)

Implementation plan:
merge
  - track mode (single segment/single track/none)
trim (by timestamp)
  - perhaps we should call this filter (include positioning?)
split (by time period days/hours)
  split 1d -tz America/Pactific
split (distance)
supplement
stops - generate stops


TOD0:
  - pretty print XML 
  - technically XML schema has elements for route/track/wpt as sequence and thus they must be ordered - pah!
  - outputted file not rendering in Google Earth
  - implemented __getitem__ but not __setitem__ (OK)
  - distance includes elevation

v2
  - parse using SAX events - allow parsing to provide filters which avoid construction of whole parts of tree altogether (only interested in tracks/wpt/routes etc) - Filter by date, etc... 
  - write using direct XML writes