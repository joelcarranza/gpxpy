#!/usr/bin/env python
# encoding: utf-8
"""
trim.py

Created by Joel Carranza on 2011-02-14.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import argparse
import GPX
import gpxkml
import xml.etree.ElementTree as ET
from itertools import groupby
from KmlFactory import KmlFactory

styleMap = dict(Lake='#water',
  Reservoir='#water',
  Stream='#water',
  Spring='#water',
  Trail="#trail",
#  Building="#building",
  Summit='#mtn',
#  Gap='#mtn'
)


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Trim GPX file to time')
  parser.add_argument('-i', metavar='file',type=argparse.FileType('rU'),default=sys.stdin)
  parser.add_argument('-o', metavar='file',type=argparse.FileType('w'),default=sys.stdout)
  args = parser.parse_args()
  gpx = GPX.GPX()
  gpx.load(args.i)
  kml = gpxkml.kml()
  w= gpxkml.KMLWriter(kml)
  w.document(name="GNIS Features")
  bounds = gpx.bounds()
#  w.append(KmlFactory.Region(
#  KmlFactory.LatLonAltBox(north=bounds[2],south=bounds[0],east=bounds[3],west=bounds[1]),
#    KmlFactory.Lod(minLodPixels=5000,minFadeExtent=1000)
#  ))
  w.iconStyle('water','http://maps.google.com/mapfiles/kml/pal4/icon25.png',color="a0ffc0c0",scale=0.5)
  w.iconStyle('mtn','http://maps.google.com/mapfiles/kml/pal4/icon60.png',scale=0.75)
#  w.iconStyle('building','http://maps.google.com/mapfiles/ms/micons/building.png',scale=0.5)
  w.iconStyle('trail','http://maps.google.com/mapfiles/ms/micons/trail.png',scale=0.75)
  w.iconStyle('default','http://maps.google.com/mapfiles/kml/pal4/icon24.png',scale=0.5)
  
  for t,wpts in groupby(sorted(gpx.waypoints,key=lambda w:(w.type,w.name)), lambda w:w.type):
    w.folder(t)
 #   if t == 'Summit':
#      w.append(KmlFactory.Region(
#      KmlFactory.LatLonAltBox(north=bounds[2],south=bounds[0],east=bounds[3],west=bounds[1]),
#        KmlFactory.Lod(minLodPixels=1000,minFadeExtent=100)
#      ))
    for wpt in wpts:
      w.waypoint(wpt,style=styleMap.get(wpt.type,'#default'))
    w.parent()
  ET.ElementTree(kml).write(args.o)
