#!/usr/bin/env python
# encoding: utf-8
"""
GPX.py

Created by Joel Carranza on 2011-02-06.
"""

import xml.etree.cElementTree as ElementTree
from xml.etree.cElementTree import Element,SubElement
import sys
import os
# this is going to fail on 2.5???
import dateutil.parser
import math

_route_scheme = _track_scheme = dict(name="s",
  cmt="s",
  desc="s",
  src="s",
  link="s")

_wpt_scheme = dict(ele="n",
  time="d",
  magvar="n",
  geoidheight="n",
  name="s",
  cmt="s",
  desc="s",
  src="s",
  link="s",
  sym="s",
  type="s",
  fix="s",
  sat="i",
  hdop="n",
  vdop="n",
  pdop="n")

NS_1_0 = 'http://www.topografix.com/GPX/1/0'
NS = NS_1_1 = 'http://www.topografix.com/GPX/1/1'
VERSION = "0.1"

def parse(source):
  "Construct a new GPX instance based on a file"
  gpx = GPX()
  gpx.load(source)
  return gpx

def wptbounds(pts):
  "return a bounding box which contains all waypoints on this path"
  # TODO: this requires a list and it would be better if we just did it in one loop
  if not pts:
    return None
  lat = [p.lat for p in pts]
  lon = [p.lon for p in pts]
  return (min(lat),min(lon),max(lat),max(lon))

def wpttimespan(pts):
  "return upper and lower bounds on the time"
  t = [p.time for p in pts if p.time is not None]
  return (min(t),max(t)) if t else None

# TODO: math!
# http://www.movable-type.co.uk/scripts/latlong.html
# dist2d
# dist3d
# See also: http://megocode3.wordpress.com/2008/02/05/haversine-formula-in-c/
# "When a difference in altitude is smallish relative to the great circle distance, a quick approximation is to add the two. This is essentially the approximation of a right triangle’s hypotenuse by adding the lengths of the two legs, reliable when one leg is much longer than the other. If the two distances were similar in magnitude, the Pythagorean formula would be more accurate, i.e. the square root of the square of altitude difference plus the square of the great circle distance."
# http://www.gps-forums.net/distance-between-two-points-t34357.html
# interpolate! Possibly not that, instead its give me n points ever mile along line
# distance from line (Cross-track distance?)
# containment within polygon
# UTM - to - LatLon (HARD!!!!)

# TODO: copy() method for all classes

class GPX:
  """
  Model of a GPX file. Gpx file contains one or more of
  the following types
  tracks
  waypoints
  routes
  metadata see http://www.topografix.com/GPX/1/1/#type_metadataType
  """

# TODO: these are pulled from metadata element  
  name = None
  desc = None
  
  def __init__(self):
    self.tracks = []
    self.waypoints = []
    self.routes = []
  
  def load(self,src):
    parser = GPXParser(self)
    parser.parse(src)
  
  def newTrack(self,**kwargs):
    t = Track(**kwargs)
    self.tracks.append(t)
    return t

  def newWaypoint(self,lat,lon,**kwargs):
    w = Waypoint(lat,lon,**kwargs)
    self.waypoints.append(w)
    return w
    
  def newRoute(self,**kwargs):
    r = Route(**kwargs)
    self.routes.append(w)
    return r
  
  def allpoints(self):
    for w in self.waypoints:
      yield w
    for r in self.routes:
      for w in r:
        yield w
    for t in self.tracks:
      for w in t.points():
        yield w

  def filter(self,pred):
    self.waypoints[:] = filter(pred,self.waypoints)
    for trk in self.tracks:
      trk.filter(pred)
    for r in self.routes:
      t.filter(pred)
    self.tracks[:] = filter(lambda t:len(t.segments()) > 0,self.tracks)
    self.routes[:] = filter(lambda t:len(r) > 0,self.routes)

  def bounds(self):
    "return a bounding box which contains all waypoints on this path"
    return wptbounds(list(self.allpoints()))

  def timespan(self):
    "return a bounding box which contains all waypoints on this path"
    return wpttimespan(list(self.allpoints()))
  
  def write(self,file):
    # note that we would like for this pretty-print possibly
    GPXWriter().write(self,file)
  
  def __str__(self):
    return "GPX{waypoints=%d,tracks=%d,routes=%d}" % (len(self.waypoints),len(self.tracks),len(self.routes))
  
class Path:
  """
  Ordered list of points. Used directly as a track segment
  and by extension for Route
  """
  
  _wpt = None
  
  def __init__(self, points=None):
    self._wpt = points if points is not None else []
  
  def points(self):
    "Return a list of waypoints in the path"
    return self._wpt
  
  def newWaypoint(self,**kwargs):
    w = Waypoint(**kwargs)
    self._wpt.append(w)
    return w
  
  def append(self,wpt):
    "Add a new waypoint to the end of the path"
    self._wpt.append(wpt)
    
  def extend(self,pts):
    "Add new waypoints to the end of the path"
    self._wpt.extend(pts)
    
  def filter(self,pred):
    "Remove point from this path based on predicate"
    self._wpt = filter(pred,self._wpt)
    
  def simplify(self,pred):
    """Remove points form path based on predicate. Predicate
    is passed two points, the current point and the last point
    that passed the test. Only points that pass the test are returned""" 
    np = self._wpt[0:1]
    for p in self._wpt[1:]:
      if pred(p,np[-1]):
        np.append(p)
    self._wpt = np
    
  def __iter__(self):
    return self._wpt.__iter__()
  
  def __len__(self):
    return len(self._wpt)
  
  def __getitem__(self,k):
    return self._wpt[k]
  
  def bounds(self):
    "return a bounding box which contains all waypoints on this path"
    return wptbounds(self._wpt)
  
  def timespan(self):
    "return min max bounds of path"
    return wpttimespan(self._wpt)
  
  def length(self):
    d = 0
    for i in xrange(1,len(self)):
      d += self[i].dist(self[i-1])
    return d
  
  def __str__(self):
    return "Path{points=%d}" % len(self._wpt)

class Route(Path):
  """
  n ordered list of waypoints representing a series of turn points leading to a destination.
  """
  
  name = None
  cmt = None
  src = None
  desc = None
  link = None
  
  def __init__(self,**kwargs):
    Path.__init__(self,**kwargs)
    for k, v in kwargs.iteritems():
       if k not in _route_scheme:
           raise TypeError("Invalid keyword argument %s" % k)
       setattr(self, k, v)
  
class Track:
  """
  Represents an ordered list of track segments (paths) which
  taken together represent a (potentially complex) path
  """
          
  name = None
  cmt = None
  src = None
  desc = None
  link = None
  _s = None
  
  def __init__(self,segments = None, points=None,**kwargs):
    self._s = segments if segments is not None else []
    if points is not None:
      self.extendpt(points)
    for k, v in kwargs.iteritems():
       if k not in _track_scheme:
           raise TypeError("Invalid keyword argument %s" % k)
       setattr(self, k, v)
  
  def points(self):
    "Returns an interator over all waypoints in track"
    # TODO: can you itertools.chain here!
    for s in self._s:
      for p in s:
        yield p
  
  def newSegment(self,**kwargs):
    p = Path(**kwargs)
    self._s.append(p)
    return p
  
  def join(self):
    "Join all segments together into a single segment"
    for s in self._s[1:]:
      self._s[0].extend(s.points)
    self._s[1:] = []
  
  # TODO: split! - given a predicate which looks at points pairwise - split around those points
  # split will sever the link between two points which fail predicate
  # it is therefor NOT useful probably for simply "cutting" a path at a point
  # where you want to perhaps duplicate a point
  def split(self,pred):
    pass
    
  def filter(self,pred):
    for s in self._s:
      s.filter(pred)
    # drop empty segments
    self._s[:] = filter(lambda s:len(s),self._s)
  
  
  def segments(self):
    return self._s
    
  def append(self,trk):
    "Add a new waypoint to the end of the path"
    self._s.append(trk)


  def extend(self,trk):
    "Add new waypoints to the end of the path"
    self._s.extend(trk)
  
  def appendpt(self,wpt):
    if not self._s:
      self.newSegment();
    self._s[-1].append(wpt)

  def extendpt(self,wpt):
    if not self._s:
      self.newSegment();
    self._s[-1].extend(wpt)
  
  def __iter__(self):
    return self._s.__iter__()

  def __len__(self):
    return len(self._s)

  def __getitem__(self,k):
    return self._s[k]
  
  def __str__(self):
    return "Track{segments=%d}" % len(self._s)
  

class Waypoint:
  """
  Represents a waypoint, point of interest, or named feature on a map.
  See: http://www.topografix.com/GPX/1/1/#type_wptType
  """
  
  
  lat = None
  lon = None
  ele = None
  time = None
  magvar = None
  geoidheight = None
  name = None
  cmt = None
  src = None
  desc = None
  link = None
  sym = None
  type = None
  fix = None
  sat = None
  hdop = None
  vdop = None
  pdop = None
  
  def __init__(self,lat=None,lon=None,**kwargs):
     self.lat = lat
     self.lon = lon
     for k, v in kwargs.iteritems():
       if k not in _wpt_scheme:
           raise TypeError("Invalid keyword argument %s" % k)
       setattr(self, k, v)
   
  def __str__(self):
    return "Waypoint{%f,%f}" % (self.lat,self.lon)
  
  def tuple2d(self):
    return (self.lon,self.lat)
    
  def tuple3d(self):
    return (self.lon,self.lat,self.ele)
    
  def dist(self,p):
    "Distance between two waypoints using haversine"
    # TODO: take into account of elevation!
    R = 6372800 # Radius of earth in meters
    lat1 = math.radians(self.lat)
    lon1 = math.radians(self.lon)
    lat2 = math.radians(p.lat)
    lon2 = math.radians(p.lon)
    dLat = lat2-lat1
    dLon = lon2-lon1
    a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(lat1) * math.cos(lat2) * math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c;

class GPXWriter:
  """
  Writes a GPX file to 
  """
  creator = "GPX.py "+VERSION

  # Taken from: http://infix.se/2007/02/06/gentlemen-indent-your-xml
  def _indent(self,elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for e in elem:
            self._indent(e, level+1)
            if not e.tail or not e.tail.strip():
                e.tail = i + "  "
        if not e.tail or not e.tail.strip():
            e.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

  def text(self,name,value):
    e = Element(name)
    e.text = value
    return e

  def textEl(self,obj,e,attr):
    for p,fmt in attr.items():
      value = getattr(obj,p)
      if value is not None:
        c = Element(p)
        if fmt == 'd':
          c.text = value.isoformat()
        else:
          c.text = str(value)
        e.append(c)

  def gpx(self,gpx):
    root = Element("gpx",xmlns=NS,version="1.1",creator=self.creator)
    for wpt in gpx.waypoints:
      root.append(self.wpt(wpt,"wpt"))
    for route in gpx.routes:
      el = self.path(route,"rte","rtept")
      self.textEl(route,el,_route_scheme)
      root.append(el) 
    for track in gpx.tracks:
      el = SubElement(root,"trk")
      self.textEl(track,el,_track_scheme)
      for seg in track:
        el.append(self.path(seg,"trkseg","trkpt"))
    return root

  def wpt(self,wpt,name):
   "Creates an XML element with specified name which represents this Waypoint"
   e = Element(name,{"lat":str(wpt.lat),"lon":str(wpt.lon)})
   self.textEl(wpt,e,_wpt_scheme)
   return e

  def path(self,p,name,ptname):
    e = Element(name)
    for p in p._wpt:
      e.append(self.wpt(p,ptname))
    return e

  def write(self,gpx,file):
    root = self.gpx(gpx)
    self._indent(root)
    ElementTree.ElementTree(root).write(file)

class GPXParser:
  """
  DOM Parsing tool which constructs a 
  """
  def __init__(self,gpx):
    self.gpx = gpx

  def mapEl(self,obj,e,attr):
    for k,fmt in attr.items():
      child = e.find("{%s}%s" % (self.NS,k))
      if child is not None:
        if fmt == 's':
          setattr(obj,k,child.text)
        elif fmt == 'd':
          setattr(obj,k,dateutil.parser.parse(child.text))
        elif fmt == 'i':
          setattr(obj,k,int(child.text))
        elif fmt == 'n':
          setattr(obj,k,float(child.text))
        else:
          raise Error("Unknown format")
      else:
        setattr(obj,k,None) 

  def parse(self,src):
    root = ElementTree.parse(src).getroot()
    # namespace should be either gpx1/0 or gpx1/1
    self.NS = root.tag[1:-4]
    for wptEl in root.findall("{%s}wpt" % self.NS):
      self.gpx.waypoints.append(self.parseWaypoint(wptEl))
    for rteEl in root.findall("{%s}rte" % self.NS):
      self.gpx.routes.append(self.parseRoute(rteEl))
    for trkEl in root.findall("{%s}trk" % self.NS):
      self.gpx.tracks.append(self.parseTrack(trkEl))

  def parseTrack(self,el):
    trk = Track()
    for seg in el.findall("{%s}trkseg" % self.NS):
      p = Path()
      for wpel in seg.findall("{%s}trkpt" % self.NS):
        p.append(self.parseWaypoint(wpel))
      trk.append(p)
    self.mapEl(trk,el,_track_scheme)
    return trk

  def parseRoute(self,el):
    r = Route()
    for wpel in el.findall("{%s}rtept" % self.NS):
      r.append(self.parseWaypoint(wpel))
    self.mapEl(r,el,_route_scheme)
    return r


  def parseWaypoint(self,e):
    pt = Waypoint()
    pt.lat = float(e.attrib['lat'])
    pt.lon = float(e.attrib['lon'])
    self.mapEl(pt,e,_wpt_scheme)
    return pt

if __name__ == '__main__':
  import sys
  for fn in sys.argv[1:]:
    gpx = GPX()
    gpx.load(fn)
    print fn
    print "------------"
    print "%d waypoints" % len(gpx.waypoints)
    print "%d tracks" % len(gpx.tracks)
    for t in gpx.tracks:
      print t.name
      for s in t:
        print "Pt count: %d" % len(s)
        print s.timespan()
        print s.bounds()
        print s.length()

