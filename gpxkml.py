#!/usr/bin/env python
# encoding: utf-8
"""
gpx2kml.py

Created by Joel Carranza on 2011-02-19.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import argparse
import GPX
import functools
import xml.etree.ElementTree as ET
from KmlFactory import KmlFactory
K = KmlFactory

def kml():
  return K.kml(dict(xmlns='http://www.opengis.net/kml/2.2'))

def _wptstring(wpt):
  return "%f,%f,0" % (wpt.lon,wpt.lat)

class KMLWriter():
  """docstring for KMLWriter"""
  
  def __init__(self,root):
    self._root = [root]
  
  def document(self,**attr):
    attr = self._fattr(**attr)
    f = K.Document(**attr)
    self._append(f)
    self._root.append(f)

  def folder(self,name,**attr):
    attr = self._fattr(name=name,**attr)
    f = K.Folder(**attr)
    self._append(f)
    self._root.append(f)

  def parent(self):
    self._root.pop()

  def _append(self,el):
    self._root[-1].append(el)
    
  def _fattr(self,name=None,description=None,style=None):
    result = {}
    if name is not None:
      result['name'] = name
    if description is not None:
      result['description'] = descriopton
    if style is not None:
      result['styleUrl'] = style
    return result
    
  def waypoint(self,wpt,**attr):
    if 'name' not in attr:
        attr['name'] = wpt.name 
    if 'style' not in attr:
        attr['style'] = "#gpx-waypoint"
    attr = self._fattr(**attr)
    attr = dict(name=name,description=description,styleUrl=style)
    self._append(K.Placemark(
      K.Point(coordinates=_wptstring(wpt)),
      ))
  
  def lineStyle(self,id,color,width=1):
    self._append(K.Style(dict(id=id),K.LineStyle(color=color,width=width)))
  
  def iconStyle(self,id,href,color=None,scale=1):
    pass
  
  def track(self,track,**attr):
    if 'name' not in attr:
        attr['name'] = track.name 
    if 'style' not in attr:
        attr['style'] = "#gpx-track"
    attr = self._fattr(**attr)
    self._append(K.Placemark(
      K.LineString(coordinates="\n".join(map(_wptstring,track.points()))),
      **attr
    ))

  def route(self,rte):
    if 'name' not in attr:
        attr['name'] = rte.name 
    if 'style' not in attr:
        attr['style'] = "#gpx-route"
    attr = self._fattr(**attr)
    self._append(K.Placemark(
      K.LineString(coordinates="\n".join(map(_wptstring,rte.points()))),
      **attr
    ))
    
  def gpx(self,gpx,createFolders=True):
    if gpx.waypoints:
      if createFolders:
        self.folder("Waypoints")
      for w in gpx.waypoints:
        self.waypoint(w)
      if createFolders:
        self.parent()
    
    if gpx.tracks:
      if createFolders:
        self.folder("Tracks")
      for t in gpx.tracks:
        self.track(t)
      if createFolders:
        self.parent()
    
    if gpx.routes:
      if createFolders:
        self.folder("Routes")
      for r in gpx.routes:
        self.route(t)
      if createFolders:
        self.parent()

def _indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for e in elem:
            _indent(e, level+1)
            if not e.tail or not e.tail.strip():
                e.tail = i + "  "
        if not e.tail or not e.tail.strip():
            e.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
                    
if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Trim GPX file to time')
  parser.add_argument('-i', metavar='file',type=argparse.FileType('r'),default=sys.stdin)
  parser.add_argument('-o', metavar='file',type=argparse.FileType('w'),default=sys.stdout)
#  parser.add_argument('-f', type=bool,default=True)
  args = parser.parse_args()
  gpx = GPX.GPX()
  gpx.load(args.i)
  
  kml = kml()
  w= KMLWriter(kml)
  w.document()
  w.iconStyle("gpx-waypoint","")
  w.lineStyle("gpx-track","ffff0000")
  w.lineStyle("gpx-route","ffff0000")
  w.gpx(gpx)
  _indent(kml)
  ET.ElementTree(kml).write(args.o)