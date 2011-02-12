#!/usr/bin/env python
# encoding: utf-8
"""
GPX.py

Created by Joel Carranza on 2011-02-06.
"""

import xml.etree.ElementTree as ElementTree
from xml.etree.ElementTree import Element
import sys
import os
# this is going to fail on 2.5???
import dateutil.parser
import math

class GPXParser:
  NS = '{http://www.topografix.com/GPX/1/1}'
  
  def __init__(self,gpx):
    self.gpx = gpx
    
  def mapEl(self,obj,e,attr):
    for k,fmt in attr.items():
      child = e.find(self.NS+k)
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
    self.NS = root.tag[0:-3]
    for wptEl in root.findall("%swpt" % self.NS):
      self.gpx.waypoints.append(self.parseWaypoint(wptEl))
    for rteEl in root.findall("%srte" % self.NS):
      self.gpx.routes.append(self.parseRoute(rteEl))
    for trkEl in root.findall("%strk" % self.NS):
      self.gpx.tracks.append(self.parseTrack(trkEl))
    
  def parseTrack(self,el):
    trk = Track()
    for seg in el.findall("%strkseg" % self.NS):
      p = Path()
      for wpel in seg.findall("%strkpt" % self.NS):
        p.append(self.parseWaypoint(wpel))
      trk.append(p)
    self.mapEl(trk,el,{
      "name":"s",
      "cmt":"s",
      "desc":"s",
      "src":"s",
      "link":"s",
    })
    return trk
  
  def parseRoute(self,el):
    trk = Route()
    for wpel in el.findall("%srtept" % self.NS):
      trk.points.append(self.parseWaypoint(wpel))
    self.mapEl(trk,el,{
      "name":"s",
      "cmt":"s",
      "desc":"s",
      "src":"s",
      "link":"s",
    })
    return trk


  def parseWaypoint(self,e):
    pt = Waypoint()
    pt.lat = float(e.attrib['lat'])
    pt.lon = float(e.attrib['lon'])
    self.mapEl(pt,e,{
      "ele":"n",
      "time":"d",
      "magvar":"d",
      "geoidheight":"d",
      "name":"s",
      "cmt":"s",
      "desc":"s",
      "src":"s",
      "link":"s",
      "sym":"s",
      "type":"s",
      "fix":"s",
      "sat":"i",
      "hdop":"d",
      "vdop":"d",
      "pdop":"d",
    })
    return pt

class GPX:
  
  def __init__(self):
    self.tracks = []
    self.waypoints = []
    self.routes = []
  
  def load(self,src):
    parser = GPXParser(self)
    parser.parse(src)
  
  def toxml(self):
    root = Element("gpx",{"xmlns":"http://www.topografix.com/GPX/1/1"})
    for wpt in self.waypoints:
      root.append(wpt.toxml("wpt"))
    for route in self.routes:
      root.append(route.toxml("rte","rtept"))    
    for track in self.tracks:
      trk = Element("trk")
      name = Element("name")
      name.text = track.name
      trk.append(name)
      for seg in track:
        trk.append(seg.toxml("trkseg","trkpt"))
      root.append(trk)
    return root
    
  def write(self,file):
    # note that we would like for this pretty-print possibly
    ElementTree.ElementTree(self.toxml()).write(file)
  
  def __str__(self):
    return "GPX{waypoints=%d,tracks=%d,routes=%d}" % (len(self.waypoints),len(self.tracks),len(self.routes))
  
class Path:
  """
  Ordered list of points
  """
  _wpt = None
  
  def __init__(self):
    self._wpt = []
  
  def points(self):
    "Return a list of waypoints in the path"
    return self._wpt
    
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
    if len(self._wpt) == 0:
      return None
    lat = [p.lat for p in self._wpt]
    lon = [p.lon for p in self._wpt]
    return (min(lat),min(lon),max(lat),max(lon))
  
  def timespan(self):
    "return min max bounds of path"
    t = [p.time for p in self._wpt if p.time is not None]
    if len(t) > 0:
      return (min(t),max(t))
    else:
      return None
  
  def toxml(self,name,ptname):
    e = Element(name)
    for p in self._wpt:
      e.append(p.toxml(ptname))
    return e
    
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
  
  def __init__(self):
    self._s = []
  
  def points(self):
    "Returns an interator over all waypoints in track"
    for s in self._s:
      for p in s:
        yield p
  
  def join(self):
    "Join all segments together into a single segment"
    for s in self._s[1:]:
      self._s[0].extend(s.points)
    self._s[1:] = []
  
  def segments(self):
    return self._s
    
  def append(self,trk):
    "Add a new waypoint to the end of the path"
    self._s.append(trk)

  def extend(self,trk):
    "Add new waypoints to the end of the path"
    self._s.extend(trk)
  
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
  #type = None
  fix = None
  sat = None
  hdop = None
  vdop = None
  pdom = None
  
  def __init__(self,lat=None,lon=None):
     self.lat = lat
     self.lon = lon
     
  def toxml(self,name):
    "Creates an XML element with specified name which represents this Waypoint"
    e = Element(name,{"lat":str(self.lat),"lon":str(self.lon)})
    return e
    
  def __str__(self):
    return "Waypoint{%d,%d}" % (self.lat,self.lon)
  
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
      for s in t.segments:
        print s.bounds()
        print s.timespan()

