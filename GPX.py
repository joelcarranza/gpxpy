#!/usr/bin/env python
# encoding: utf-8
"""
untitled.py

Created by Joel Carranza on 2011-02-06.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import xml.etree.ElementTree as ElementTree
from xml.etree.ElementTree import Element
import sys
import os
import dateutil.parser

NS = '{http://www.topografix.com/GPX/1/1}'

def mapEl(obj,e,attr):
  for k,fmt in attr.items():
    child = e.find(NS+k)
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

def parseTrack(el):
  trk = Path()
  for wpel in el.findall("%strkseg/%strkpt" % (NS,NS)):
    trk.points.append(parseWaypoint(wpel))
  mapEl(trk,el,{
    "name":"s",
    "cmt":"s",
    "desc":"s",
    "src":"s",
    "link":"s",
  })
  return trk
  
def parseRoute(el):
  trk = Path()
  for wpel in el.findall("%srtept" % NS):
    trk.points.append(parseWaypoint(wpel))
  mapEl(trk,el,{
    "name":"s",
    "cmt":"s",
    "desc":"s",
    "src":"s",
    "link":"s",
  })
  return trk


def parseWaypoint(e):
  pt = Waypoint()
  pt.lat = float(e.attrib['lat'])
  pt.lon = float(e.attrib['lon'])
  mapEl(pt,e,{
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
    root = ElementTree.parse(src).getroot()
    for wptEl in root.findall("%swpt" % NS):
      self.waypoints.append(parseWaypoint(wptEl))
    for rteEl in root.findall("%srte" % NS):
      self.routes.append(parseRoute(trkEl))
    for trkEl in root.findall("%strk" % NS):
      self.tracks.append(parseTrack(trkEl))
  
  
  def toxml(self):
    root = Element("gpx",{"xmlns":"http://www.topografix.com/GPX/1/1"})
    for wpt in self.waypoints:
      root.append(wpt.toxml("wpt"))
    for route in self.routes:
      root.append(route.toxml("rte"))    
    for track in self.tracks:
      root.append(track.toxml("trk"))
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
    e = Element(name,{"lat":str(self.lat),"lon":str(self.lon)})
    return e

def main():
  gpx = GPX()
  gpx.load("data/track.gpx")

if __name__ == '__main__':
  main()

