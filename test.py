"""Unit test for GPX.py"""

from gpxpy import *
import unittest
import StringIO
import math


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
    self.assertEquals(len(self.gpx.waypoints),0)
    self.assertEquals(len(self.gpx.routes),0)
    
  def testTrackIter(self):
    trk = self.gpx.tracks[0]
    self.assertEquals(len(trk),1)
    # points of track is not a list - it is a generator!
    self.assertEquals(len([x for x in trk.points()]),3)

  def testSegmentIter(self):
    seg = self.gpx.tracks[0][0]
    self.assertEquals(len(seg),3)
    self.assertEquals(seg[0].lat,47.644548)
    self.assertEquals(seg[0].lon,-122.326897)
  
  def testSegmentFilter(self):
    seg = self.gpx.tracks[0][0]
    seg.filter(lambda x:True)
    self.assertEquals(len(seg),3)
    seg.filter(lambda x:False)
    self.assertEquals(len(seg),0)
  
  def testSegmentFilter(self):
    seg = self.gpx.tracks[0][0]
    seg.simplify(lambda a,b:math.fabs(a.ele-b.ele) > 1)
    self.assertEquals(len(seg),2)
  
  def testTimestamp(self):
    seg = self.gpx.tracks[0][0]
    assert seg.timespan() is not None
  
  def testBounds(self):
    seg = self.gpx.tracks[0][0]
    assert seg.bounds() is not None
    
  def testFilter(self):
    self.gpx.filter(lambda x:False)
    self.assertEquals(len(self.gpx.waypoints),0)
    self.assertEquals(len(self.gpx.tracks),0)
    self.assertEquals(len(self.gpx.routes),0)
    
class WaypointTest(unittest.TestCase):
  def testDist(self):
    # result taken from http://en.wikipedia.org/wiki/Great-circle_distance
    d = Waypoint(36.12,-86.67).dist(Waypoint(33.94,-118.40))
    self.assertAlmostEquals(d,2887260,0)

class WriteTest(unittest.TestCase):
  def testWrite(self):
    g = GPX()
    g.waypoints.append(Waypoint(47.644548,-122.326897))
    p = Path()
    p.append(Waypoint(47.644548,-122.326897))
    t = Track()
    t.append(p)
    g.tracks.append(t)
    s = StringIO.StringIO()
    g.write(s)
    print s.getvalue()
    g2 = GPX()
    g2.load(StringIO.StringIO(s.getvalue()))
    self.assertEquals(len(g2.waypoints),1)
  
if __name__ == "__main__":
  unittest.main()