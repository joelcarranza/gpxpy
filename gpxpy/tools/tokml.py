#!/usr/bin/env python
# encoding: utf-8
"""
gpxkml.py

Converts gpx files to KML

Created by Joel Carranza on 2011-02-19.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import argparse
import isodate
from gpxpy import GPX
import functools
import xml.etree.ElementTree as ET

ET._namespace_map['http://www.google.com/kml/ext/2.2'] = 'gx'

# TODO: this should go into tokml!
# Taken from http://effbot.org/zone/element-builder.htm
class _K(object):

    def __call__(self, tag, *children, **attrib):
        elem = ET.Element(tag)
        for key,value in attrib.items():
          c = ET.SubElement(elem,key)
          c.text = str(value)
        for item in children:
            if isinstance(item, dict):
                elem.attrib.update(item)
            elif isinstance(item, basestring):
                if len(elem):
                    elem[-1].tail = (elem[-1].tail or "") + item
                else:
                    elem.text = (elem.text or "") + item
            elif ET.iselement(item):
                elem.append(item)
            else:
                raise TypeError("bad argument: %r" % item)
        return elem

    def __getattr__(self, tag):
        return functools.partial(self, tag)

# create factory object
K = _K()

def _wptstring(wpt):
  return "%f,%f,0" % (wpt.lon,wpt.lat)

class KMLWriter():
  """docstring for KMLWriter"""
  
  
  
  def __init__(self,root):
    self._root = [root]
    self.gxTracks = True
  
  def document(self,**attr):
    attr = self._fattr(**attr)
    f = K.Document(**attr)
    self.append(f)
    self._root.append(f)

  def folder(self,name,**attr):
    attr = self._fattr(name=name,**attr)
    f = K.Folder(**attr)
    self.append(f)
    self._root.append(f)

  def parent(self):
    self._root.pop()

  def append(self,el):
    self._root[-1].append(el)
  
  def _fattr(self,name=None,description=None,style=None):
    result = {}
    if name is not None:
      result['name'] = name
    if description is not None:
      result['description'] = description
    if style is not None:
      result['styleUrl'] = style
    return result
    
  def waypoint(self,wpt,**attr):
    if 'name' not in attr:
        attr['name'] = wpt.name 
    if 'style' not in attr:
        attr['style'] = "#gpx-waypoint"
    if 'description' not in attr:
        attr['description'] = wpt.desc or ''
    attr = self._fattr(**attr)
    el = K.Placemark(
      K.Point(coordinates=_wptstring(wpt)),
      **attr)
    if wpt.time:
      el.append(K.TimeStamp(when=isodate.datetime_isoformat(wpt.time)))
    self.append(el)
  
  def lineStyle(self,id,color,width=1,labelColor=None, labelScale=None):
    style = K.Style(dict(id=id))
    style.append(K.LineStyle(color=color,width=width))
    if labelColor is not None or labelScale is not None:
      style.append(K.LabelStyle(color=color if labelColor else "ffffffff",scale=labelScale if labelScale else 1.0))
    self.append(style)
  
  def iconStyle(self,id,href,color=None,scale=1,labelColor=None,labelScale=None):
    attr = dict(scale=scale)
    if color is not None:
      attr['color'] = color
    style = K.Style(dict(id=id))
    style.append(K.IconStyle(K.Icon(href=href),**attr))
    if labelColor is not None or labelScale is not None:
      style.append(K.LabelStyle(color=color if labelColor else "ffffffff",scale=labelScale if labelScale else 1.0))
    self.append(style)
  
  def track_path(self,pl,points):
     if self.gxTracks:
        trk = ET.SubElement(pl,'{http://www.google.com/kml/ext/2.2}Track')
        for w in points:
          ET.SubElement(trk,'when').text = isodate.datetime_isoformat(w.time)
        for w in points:
          ET.SubElement(trk,'{http://www.google.com/kml/ext/2.2}coord').text = " ".join(map(str,w.tuple3d()))
     else:
        pl.append(K.LineString(coordinates="\n".join(map(_wptstring,points))))
        
  def track(self,track,**attr):
    if 'name' not in attr:
        attr['name'] = track.name 
    if 'style' not in attr:
        attr['style'] = "#gpx-track"
    
    if len(track) == 1:
      # TODO: supply 
      fattr = self._fattr(**attr)
      pl = K.Placemark(
        **fattr
      )
      self.track_path(pl,list(track.points()))
      self.append(pl)
    else:
      self.folder(track.name)
      lastp = None
      for s in track:
        # TODO: number and name!
        fattr = self._fattr(**attr)
        pl = K.Placemark(
          **fattr
        )
        self.track_path(pl,list(s))
        self.append(pl)
        if lastp:
          pl = K.Placemark(styleUrl='#gpx-track-missing')
          self.track_path(pl,[lastp,s[0]])
          self.append(pl)
        lastp = s[-1]
        
      self.parent()

  def route(self,rte,**attr):
    if 'name' not in attr:
        attr['name'] = rte.name 
    if 'style' not in attr:
        attr['style'] = "#gpx-route"
    attr = self._fattr(**attr)
    self.append(K.Placemark(
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
        self.route(r)
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

def parse_color(colorstring):
  "parse a string of format RRGGBB(AA)?"
  if colorstring[0] == '#': colorstring = colorstring[1:]
  if len(colorstring) != 6 and len(colorstring) != 8:
    raise ValueError, "input #%s is not in #RRGGBB(AA)? format" % colorstring
  r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:6]
  if len(colorstring) > 6:
    a = colorstring[6:]
  else:
    a = 'ff'
  return a+b+g+r
                    
def run():
  parser = argparse.ArgumentParser(description='Generate KML from a GPX file')
  parser.add_argument('-i', metavar='file',
    type=argparse.FileType('r'),default=sys.stdin,help="GPX file to process. If none is specified STDIN will be use")
  parser.add_argument('-o', metavar='file',
    type=argparse.FileType('w'),default=sys.stdout,help="file name of resulting KML file. If none is specified STDOUT will be used")
  parser.add_argument('--kml-name',dest='kmlname')
  parser.add_argument('--kml-desc',dest='kmldesc')
  # TODO: move these defaults to constants at top of file
  parser.add_argument('-wpt-icon',dest='wpticon',
    default='http://maps.google.com/mapfiles/ms/micons/ylw-pushpin.png')
  parser.add_argument('-wpt-scale',dest='wptscale',type=float,default=1.0)

  # TODO: this should support a list of colors
  # which we rotate through 
  parser.add_argument('-track-color',dest='trkcolor',type=parse_color,default='#ff7e00')
  parser.add_argument('-track-width',dest='trkwidth',type=int,default=3)

  # TODO: this should support a list of colors
  # which we rotate through 
  parser.add_argument('-route-color',dest='routecolor',type=parse_color,default='#ff7e00')
  parser.add_argument('-route-width',dest='routewidth',type=int,default=3)
  
  args = parser.parse_args()
  gpx = GPX()
  gpx.load(args.i)
  
  kml = K.kml(dict(xmlns='http://www.opengis.net/kml/2.2'))
  w= KMLWriter(kml)
  w.document(name=args.kmlname,description=args.kmldesc)
  w.iconStyle("gpx-waypoint",args.wpticon,args.wptscale)
  w.lineStyle("gpx-track",args.trkcolor,args.trkwidth)
  w.lineStyle("gpx-track-missing","cccccccc",args.trkwidth)
  w.lineStyle("gpx-route",args.routecolor,args.routewidth)
  w.gpx(gpx)
  _indent(kml)
  ET.ElementTree(kml).write(args.o)
  
if __name__ == "__main__":
  run()

