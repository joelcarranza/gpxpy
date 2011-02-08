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
import dateutil.parser


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
      self.gpx.routes.append(self.parseRoute(trkEl))
    for trkEl in root.findall("%strk" % self.NS):
      self.gpx.tracks.append(self.parseTrack(trkEl))
    
  def parseTrack(self,el):
    trk = Path()
    for wpel in el.findall("%strkseg/%strkpt" % (self.NS,self.NS)):
      trk.points.append(self.parseWaypoint(wpel))
    self.mapEl(trk,el,{
      "name":"s",
      "cmt":"s",
      "desc":"s",
      "src":"s",
      "link":"s",
    })
    return trk
  
  def parseRoute(self,el):
    trk = Path()
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
      root.append(route.toxml("rte"))    
    for track in self.tracks:
      trk = Element("trk")
      trk.append(track.toxml("trkseg"))
      root.append(trk)
    return root
    
  def write(self,file):
    ElementTree.ElementTree(self.toxml()).write(file)
  
class Path:
  points = None
  name = None
  cmt = None
  src = None
  desc = None
  link = None
  
  def __init__(self):
    self.points = []
  
  def bounds(self):
    "return a bounding box which contains all waypoints on this path"
    if len(self.points) == 0:
      return None
    lat = [p.lat for p in self.points]
    lon = [p.lon for p in self.points]
    return (min(lat),min(lon),max(lat),max(lon))
  
  def timespan(self):
    t = [p.time for p in self.points if p.time is not None]
    if len(t) > 0:
      return (min(t),max(t))
    else:
      return None
  
  def toxml(self,name):
    e = Element(name)
    for p in self.points:
      e.append(p.toxml(name+"pt"))
    return e

class Waypoint:
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
      print t.bounds()
      print t.timespan()

