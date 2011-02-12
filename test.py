"""Unit test for GPX.py"""

from GPX import GPX
from GPX import Path
from GPX import Track
from GPX import Route
from GPX import Waypoint
import unittest
import StringIO


class ParseTest(unittest.TestCase):
  xml = """<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
  <gpx xmlns="http://www.topografix.com/GPX/1/1" xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" creator="Oregon 400t" version="1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.garmin.com/xmlschemas/GpxExtensions/v3 http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd">
    <metadata>
      <link href="http://www.garmin.com">
        <text>Garmin International</text>
      </link>
      <time>2009-10-17T22:58:43Z</time>
    </metadata>
    <trk>
      <name>Example GPX Document</name>
      <trkseg>
        <trkpt lat="47.644548" lon="-122.326897">
          <ele>4.46</ele>
          <time>2009-10-17T18:37:26Z</time>
        </trkpt>
        <trkpt lat="47.644548" lon="-122.326897">
          <ele>4.94</ele>
          <time>2009-10-17T18:37:31Z</time>
        </trkpt>
        <trkpt lat="47.644548" lon="-122.326897">
          <ele>6.87</ele>
          <time>2009-10-17T18:37:34Z</time>
        </trkpt>
      </trkseg>
    </trk>
  </gpx>"""
  
  def setUp(self):
    self.gpx = GPX()
    self.gpx.load(StringIO.StringIO(self.xml))
    print self.gpx
  
  def testSimpleParse(self):
    self.assertEquals(len(self.gpx.tracks),1)
    self.assertEquals(len(self.gpx.tracks[0].segments[0].points),3)
    self.assertEquals(self.gpx.tracks[0].segments[0].points[0].lat,47.644548)
    self.assertEquals(self.gpx.tracks[0].segments[0].points[0].lon,-122.326897)
  
  def testTimestamp(self):
    assert self.gpx.tracks[0].segments[0].timespan() is not None
  
  def testBounds(self):
    assert self.gpx.tracks[0].segments[0].bounds() is not None
    


class WriteTest(unittest.TestCase):
  def testWrite(self):
    g = GPX()
    g.waypoints.append(Waypoint(47.644548,-122.326897))
    p = Path()
    p.points.append(Waypoint(47.644548,-122.326897))
    t = Track()
    t.segments.append(p)
    g.tracks.append(t)
    s = StringIO.StringIO()
    g.write(s)
    print s.getvalue()
    g2 = GPX()
    g2.load(StringIO.StringIO(s.getvalue()))
    self.assertEquals(len(g2.waypoints),1)
  
if __name__ == "__main__":
  unittest.main()