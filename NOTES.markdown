GPXPY - a set of tools for dealing with GPX files

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
Prune very shirt tracks
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

TOD0:
  - track can contain multiple trkseg, not supported right now
  
