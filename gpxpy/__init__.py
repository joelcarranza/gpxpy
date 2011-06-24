#!/usr/bin/env python
# encoding: utf-8
"""
gpxpy 

Python API for working with GPX files. 

Created by Joel Carranza on 2011-02-06.
"""

import xml.etree.cElementTree as ElementTree
from xml.etree.cElementTree import Element,SubElement
import sys
import os
import math
import bisect
from xmlutil import XAttr as xa
import xmlutil

__version_info__ = ('0', '1')
__version__ = '.'.join(__version_info__)

NS_1_0 = 'http://www.topografix.com/GPX/1/0'
NS = NS_1_1 = 'http://www.topografix.com/GPX/1/1'

def parse(source):
  "Construct a new GPX instance based on a file object"
  gpx = GPX()
  gpx.load(source)
  return gpx

def wptdistance(pts):
  "Determine a total path distance for a list of waypoints"
  # does there exist some pairwise function?
  d = 0
  for ix in xrange(1,len(pts)):
    d += pts[ix].dist(pts[ix-1])
  return d

def wptbounds(pts):
  "return a bounding box which contains all waypoints on this path"
  if not pts:
    return None
  lat = [p.lat for p in pts]
  lon = [p.lon for p in pts]
  return (min(lat),min(lon),max(lat),max(lon))

def wpttimespan(pts):
  "return upper and lower bounds on the time for a list of points"
  t = [p.time for p in pts if p.time is not None]
  return (min(t),max(t)) if t else None

class GPX:
  """
  Root element of a gpx file. 
  see http://www.topografix.com/GPX/1/1/#type_metadataType

  Attributes:
    tracks - List of Track(s)
    waypoints - List of Waypoint(s)
    routes - List or Route(s)
  """
  
  # TODO implement metadata!
  
  def __init__(self):
    self.name = None
    self.tracks = []
    self.waypoints = []
    self.routes = []
  
  def load(self,src):
    "Populate this GPX file from a file source"
    parser = GPXParser(self)
    parser.parse(src)
  
  def new_track(self,**kwargs):
    t = Track(**kwargs)
    self.tracks.append(t)
    return t

  def new_waypoint(self,lat,lon,**kwargs):
    w = Waypoint(lat,lon,**kwargs)
    self.waypoints.append(w)
    return w
    
  def new_route(self,**kwargs):
    r = Route(**kwargs)
    self.routes.append(r)
    return r
  
  def segments_to_tracks(self):
    newt = []
    for t in self.tracks:
      for s in t:
        newt.append(Track(points=s))
    self.tracks = newt
    
  def allpoints(self):
    "Enumerate all waypoints in the GPX"
    for w in self.waypoints:
      yield w
    for r in self.routes:
      for w in r:
        yield w
    for t in self.tracks:
      for w in t.points():
        yield w
  
  def pt_at_time(self,dt):
    for t in self.tracks:
      for s in t:
        (mints,maxts) = s.timespan()
        if mints < dt and dt < maxts:
          return s.pt_at_time(dt)

  def join(self,maxdist=None,maxtime=None):
    "Join all segments together into a single segment"
    track = Track()
    # collapse all segments into single track
    for t in self.tracks:
      track.extend(t)
    # perform standard join
    track.join(maxdist,maxtime)
    self.tracks = [track]
    
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
  
  def new_waypoint(self,**kwargs):
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
    
  def pt_at_time(self,date):
    dts = [p.time for p in self]
    ix = bisect.bisect_left(dts,date)
    return self[ix]
  
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
    return wptdistance(self._wpt)
  
  def __str__(self):
    return "Path{points=%d}" % len(self._wpt)

class Route(Path):
  """
  An ordered list of waypoints representing a series of turn points leading to a destination. 
  See: http://www.topografix.com/GPX/1/1/#type_rteType
  """
  
  _scheme = [xa('name',type="s"),
    xa('cmt',type="s"),
    xa('desc',type="s"),
    xa('src',type="s"),
    xa('link',type="s"),
    xa('number',type='n'),
    xa('type',type='s')]
  
  def __init__(self,points=None,**kwargs):
    Path.__init__(self,points if points is not None else [])
    xmlutil.init(self,kwargs,self._scheme)
  
class Track:
  """
  Represents an ordered list of track segments (paths) which
  taken together represent a (potentially complex) path. 
  A Track Segment holds a list of Track Points which are logically connected in order. To represent a single GPS track where GPS reception was lost, or the GPS receiver was turned off, start a new Track Segment for each continuous span of track data.
  
  See: 
  http://www.topografix.com/GPX/1/1/#type_trkType
  """
          
  _scheme = [xa('name',type="s"),
    xa('cmt',type="s"),
    xa('desc',type="s"),
    xa('src',type="s"),
    xa('link',type="s"),
    xa('number',type='n'),
    xa('type',type='s')]
    
  _s = None
  
  def __init__(self,segments = None, points=None,**kwargs):
    self._s = segments if segments is not None else []
    if points is not None:
      self.extendpt(points)
    xmlutil.init(self,kwargs,self._scheme)
  
  def points(self):
    "Returns an interator over all waypoints in track"
    # TODO: can you itertools.chain here!
    for s in self._s:
      for p in s:
        yield p
        
  def bounds(self):
     "return a bounding box which contains all waypoints on this path"
     return wptbounds(list(self.points()))

  def timespan(self):
     "return a bounding box which contains all waypoints on this path"
     return wpttimespan(list(self.points()))
  
  def new_segment(self,**kwargs):
    p = Path(**kwargs)
    self._s.append(p)
    return p
  
  def tracks_from_segments(self):
    "Create a new set of tracks from the contained segments"
    return [Track(segments=[s]) for s in self._s]
  
  def split(self,pred):
    "Split track into multiple segments according to a predicate"
    allsegs = []
    for seg in self:
      currseg = None
      for wpt in seg:
        if currseg is None or not pred(currseg[-1],wpt):
          currseg = Path()
          allsegs.append(currseg)
        currseg.append(wpt)
    self._s = allsegs
  
  def join(self,maxdist=None,maxtime=None):
    "Join all segments together into a single segment"
    newseg = [self._s[0]]
    for s in self._s[1:]:
      tail = newseg[-1][-1]
      head = s[0] 
      if maxdist is not None and tail.dist(head) > maxdist:
        newseg.append(s)
      elif maxtime is not None and (head.time-tail.time) > maxtime:
        newseg.append(s)
      else:        
        newseg[-1].extend(s)
    self._s = newseg
  
  def filter(self,pred):
    for s in self._s:
      s.filter(pred)
    # drop empty segments
    self._s[:] = filter(lambda s:len(s),self._s)
  
  
  def pt_at_time(self,date):
    return min(self.points(),key=lambda p:abs(p.time-date))
  
  def length(self):
    l = 0
    for s in self:
      l += s.length()
    return l

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
      self.new_segment();
    self._s[-1].append(wpt)

  def extendpt(self,wpt):
    if not self._s:
      self.new_segment();
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
  
  _scheme = [
    xa('lat',type="n",attr=True),
    xa('lon',type="n",attr=True),
    xa('ele',type="n"),
    xa('time',type="d"),
    xa('magvar',type="n"),
    xa('geoidheight',type="n"),
    xa('name',type="s"),
    xa('cmt',type="s"),
    xa('desc',type="s"),
    xa('src',type="s"),
    # TODO: link is not a simple type
    xa('link',type="s"),
    xa('sym',type="s"),
    xa('type',type="s"),
    xa('fix',type="s"),
    xa('sat',type="i"),
    xa('hdop',type="n"),
    xa('vdop',type="n"),
    xa('pdop',type="n")]
  
  def __init__(self,lat,lon,**kwargs):
    self.lat = lat
    self.lon = lon
    xmlutil.init(self,kwargs,self._scheme[2:])
    
  def __str__(self):
    return "Waypoint{%f,%f}" % (self.lat,self.lon)
  
  def tuple2d(self):
    return (self.lon,self.lat)
    
  def tuple3d(self):
    return (self.lon,self.lat,self.ele)
    
    # http://www.movable-type.co.uk/scripts/latlong.html
    # See also: http://megocode3.wordpress.com/2008/02/05/haversine-formula-in-c/
    # "When a difference in altitude is smallish relative to the great circle distance, a quick approximation is to add the two. This is essentially the approximation of a right triangle’s hypotenuse by adding the lengths of the two legs, reliable when one leg is much longer than the other. If the two distances were similar in magnitude, the Pythagorean formula would be more accurate, i.e. the square root of the square of altitude difference plus the square of the great circle distance."
    # http://www.gps-forums.net/distance-between-two-points-t34357.html
    # interpolate! Possibly not that, instead its give me n points ever mile along line
  def dist(self,p,includeEle=False):
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
    d = R * c
    # approximate distance in 3d by adding elevation distance
    if includeEle and self.ele is not None and p.ele is not None:
      d += abs(self.ele-p.ele)
    return d

class GPXWriter:
  """
  Writes a GPX file to 
  """
  creator = "gpxpy "+__version__


  def gpx(self,gpx):
    "Construct an ElementTree for the given GPX file"
    root = Element("gpx",xmlns=NS,version="1.1",creator=self.creator)
    for wpt in gpx.waypoints:
      root.append(self.wpt(wpt,"wpt"))
    for route in gpx.routes:
      el = self.path(route,"rte","rtept")
      xmlutil.write(el,route,Route._scheme)
      root.append(el) 
    for track in gpx.tracks:
      el = SubElement(root,"trk")
      xmlutil.write(el,track,Track._scheme)
      for seg in track:
        el.append(self.path(seg,"trkseg","trkpt"))
    return root

  def wpt(self,wpt,name):
   "Creates an XML element with specified name which represents this Waypoint"
   e = Element(name)
   xmlutil.write(e,wpt,Waypoint._scheme)
   return e

  def path(self,p,name,ptname):
    e = Element(name)
    for p in p._wpt:
      e.append(self.wpt(p,ptname))
    return e

  def write(self,gpx,file):
    root = self.gpx(gpx)
    xmlutil.indent(root)
    ElementTree.ElementTree(root).write(file)

class GPXParser:
  """
  DOM Parsing tool which constructs a new GPX file
  """
  def __init__(self,gpx):
    self.gpx = gpx

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
    trk = Track(**xmlutil.parse(self.NS,el,Track._scheme))
    for seg in el.findall("{%s}trkseg" % self.NS):
      p = Path()
      for wpel in seg.findall("{%s}trkpt" % self.NS):
        p.append(self.parseWaypoint(wpel))
      trk.append(p)
    return trk

  def parseRoute(self,el):
    r = Route(**xmlutil.parse(self.NS,el,Route._scheme))
    for wpel in el.findall("{%s}rtept" % self.NS):
      r.append(self.parseWaypoint(wpel))
    return r


  def parseWaypoint(self,e):
    return Waypoint(**xmlutil.parse(self.NS,e,Waypoint._scheme))



