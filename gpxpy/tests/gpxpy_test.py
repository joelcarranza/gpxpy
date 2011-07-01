"""Unit test for GPX.py"""

from gpxpy import *
import unittest
import StringIO
import math
import gpxpy.tests

class ParseTest(unittest.TestCase):
  
  def parseTrack1(self):
    gpx = gpxpy.tests.load('track-1.gpx')
    # parsed correctly
    self.assertEquals(len(self.gpx.tracks),1)
    self.assertEquals(len(self.gpx.waypoints),0)
    self.assertEquals(len(self.gpx.routes),0)
    trk = gpx.tracks[0]
    self.assertEquals(trk.name,"Example GPX Document")
    # 1 segment, 3 points
    self.assertEquals(len(trk),1)
    self.assertEquals(len(trk.points()),3)
    self.assertEquals(len(trk[0]),3)
    
    

class Track1Test(unittest.TestCase):
   
  def setUp(self):
    self.gpx = gpxpy.tests.load('track-1.gpx')
  
  def testSimpleParse(self):
    self.assertEquals(len(self.gpx.tracks),1)
    self.assertEquals(len(self.gpx.waypoints),0)
    self.assertEquals(len(self.gpx.routes),0)
    
  def testTrackIter(self):
    trk = self.gpx.tracks[0]
    self.assertEquals(len(trk),1)
    # points of track is not a list - it is a generator!
    self.assertEquals(len(list(trk.points())),3)

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