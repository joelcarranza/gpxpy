import urllib
from xml.etree.ElementTree import parse
from datetime import datetime
import dateutil.parser
import pytz
from GPX import *

localtz = pytz.timezone("America/Los_Angeles")

gpx = GPX()
gpx.load("data/track.gpx")

min = 5

#print len(pts)
lastDate = None
filterPts = []
for t in gpx.tracks:
  for p in t.points():
  #  print p
    if lastDate is None:
      filterPts.append(p)
      lastDate = p.time
    else:
      diff = p.time-lastDate
      if diff.days > 0 or diff.seconds > min*60:
        filterPts.append(p)
        lastDate = p.time

#print len(filterPts)
#print filterPts  
# chart PT: https://chart.googleapis.com/chart?chst=d_text_outline&chld=000000|12|h|FFFFFF|b|8:32a

print """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
<Style id="pmk">
      <IconStyle>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/pal3/icon61.png</href>
        </Icon>
      </IconStyle>
</Style>
<Folder>
<name>GPX Points</name>
"""
for p in filterPts:
  name = p.time.astimezone(localtz).strftime("%m-%d %I:%M%p")
  print """<Placemark>
    <name>%s</name>
    <styleUrl>#pmk</styleUrl>
    <Point>
      <coordinates>%s,%s,0</coordinates>
    </Point>
    <TimeStamp>
      <when>%s</when>
    </TimeStamp>
  </Placemark>""" % (name,p.lon,p.lat,p.time.strftime("%Y-%m-%dT%H:%M:%SZ"))
print """
</Folder>
</Document>
</kml>"""
