"""Unit test for GPX.py"""

from gpxpy import *
import unittest
import StringIO
import math
import gpxpy.tests

class ParseTest(unittest.TestCase):
  
  def test_parse_track1(self):
    gpx = gpxpy.tests.load('track-1.gpx')
    # parsed correctly - 1 track
    self.assertEquals(len(gpx.tracks),1)
    self.assertEquals(len(gpx.waypoints),0)
    self.assertEquals(len(gpx.routes),0)
    trk = gpx.tracks[0]
    self.assertEquals(trk.name,"Example GPX Document")
    # 1 segment, 3 points
    self.assertEquals(len(trk),1)
    self.assertEquals(len(list(trk.points())),3)
    seg = trk[0]
    self.assertEquals(len(seg),3)
    # first waypoint
    wpt = seg[0]
    self.assertEquals(wpt.lat,47.644548)
    self.assertEquals(wpt.lon,-122.326897)
    self.assertEquals(wpt.ele,4.46)
    
    # test waypoints in track
    for p in trk.points():
      assert p.lat is not None
      assert p.lon is not None
      assert p.time is not None
      assert p.ele is not None
      assert p.name is None
      
  def test_parse_route1(self):
    gpx = gpxpy.tests.load('route-1.gpx')
    # parsed correctly - 1 route,19 pts
    self.assertEquals(len(gpx.tracks),0)
    self.assertEquals(len(gpx.waypoints),0)
    self.assertEquals(len(gpx.routes),1)
    rte = gpx.routes[0]
    self.assertEquals(rte.name,"Oregon to Utah")
    self.assertEquals(len(rte),19)
    # names, no times, no elevation
    for p in rte:
      assert p.name is not None
      assert p.lat is not None
      assert p.lon is not None
      assert p.time is None
      assert p.ele is None
      
  def test_parse_wpt1(self):
    gpx = gpxpy.tests.load('waypoints-1.gpx')
    # parsed correctly - 1 route,19 pts
    self.assertEquals(len(gpx.tracks),0)
    self.assertEquals(len(gpx.waypoints),7)
    self.assertEquals(len(gpx.routes),0)
    # names, no times, no elevation
    for p in gpx.waypoints:
      assert p.name is not None
      assert p.cmt is not None
      assert p.desc is not None      
      assert p.sym is not None      
      assert p.lat is not None
      assert p.lon is not None
      assert p.time is not None
      assert p.ele is not None
      

class OperationsTest(unittest.TestCase):
   
  def test_segment_filter(self):
    gpx = gpxpy.tests.load('track-1.gpx')
    seg = gpx.tracks[0][0]
    seg.filter(lambda x:True)
    self.assertEquals(len(seg),3)
    seg.filter(lambda x:False)
    self.assertEquals(len(seg),0)
    
  def test_timestamp(self):
    gpx = gpxpy.tests.load('track-1.gpx')
    seg = gpx.tracks[0][0]
    assert seg.timespan() is not None
  
  def test_bounds(self):
    gpx = gpxpy.tests.load('track-1.gpx')
    seg = gpx.tracks[0][0]
    assert seg.bounds() is not None
    
  def test_filter(self):
    gpx = gpxpy.tests.load('track-1.gpx')
    gpx.filter(lambda x:False)
    self.assertEquals(len(gpx.waypoints),0)
    self.assertEquals(len(gpx.tracks),0)
    self.assertEquals(len(gpx.routes),0)
    
class WaypointTest(unittest.TestCase):
  def test_dist(self):
    # result taken from http://en.wikipedia.org/wiki/Great-circle_distance
    d = Waypoint(36.12,-86.67).dist(Waypoint(33.94,-118.40))
    self.assertAlmostEquals(d,2887260,0)

class WriteTest(unittest.TestCase):
  def test_write(self):
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