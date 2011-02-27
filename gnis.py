#!/usr/bin/env python
# encoding: utf-8
"""
trim.py

Created by Joel Carranza on 2011-02-14.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import argparse
import re
import datetime;
from GPX import *
import pytz
from csv import DictReader
import xml.etree.ElementTree as ET

bounds = (36.559065887999999, -119.559910528, 37.872216623, -118.291351572)

def placemark(lat,lon,ele,**kwargs):
  p = ET.Element('Placemark')
  for k,v in kwargs.items():
    ET.SubElement(p,k).text = v
  geom = ET.SubElement(p,"Point")
  ET.SubElement(geom,"coordinates").text = "%f,%f" % (lon,lat)
  return p

def loadKml():
  xml = """<?xml version="1.0" encoding="UTF-8"?>
  <kml>
  <Document>
    <name>GNIS Names</name>
    <open>1</open>
    <Style id="Locale">
      <IconStyle>
        <scale>0.5</scale>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/pal4/icon24.png</href>
        </Icon>
      </IconStyle>
    </Style>
  </Document>
  </kml>"""
  return ET.fromstring(xml)

def styleIcon(id,url):
  xml = """<Style id="%s">
    <IconStyle>
      <Icon>
        <href>%s</href>
      </Icon>
    </IconStyle>
  </Style>""" % (id,url)
  return ET.fromstring(xml)

def main(files):
  kml = loadKml()
  doc = kml.find('Document')
  doc.append(styleIcon('Lake','http://labs.google.com/ridefinder/images/mm_20_blue.png'))
  doc.append(styleIcon('Resevoir','http://labs.google.com/ridefinder/images/mm_20_blue.png'))
  doc.append(styleIcon('Stream','http://labs.google.com/ridefinder/images/mm_20_blue.png'))
  doc.append(styleIcon('Spring','http://labs.google.com/ridefinder/images/mm_20_blue.png'))
  doc.append(styleIcon('Summit','http://maps.google.com/mapfiles/kml/pal3/icon29.png'))
  doc.append(styleIcon('Gap','http://maps.google.com/mapfiles/kml/pal3/icon29.png'))
  
  for f in files:
    reader = DictReader(f)
    for row in reader:
        lat = float(row['PRIM_LAT_DEC'])
        lon = float(row['PRIM_LONG_DEC'])
        name = row['FEATURE_NAME']
        featClass = row['FEATURE_CLASS']
        if bounds[0] <= lat and lat <= bounds[2] and bounds[1] <= lon and lon <= bounds[3]:
          doc.append(placemark(lat,lon,None,name=name,styleUrl="#Locale",description=featClass))
  return ET.ElementTree(kml)

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Trim GPX file to time')
  parser.add_argument('-i', metavar='file',nargs="+",type=argparse.FileType('rU'),default=sys.stdin)
  parser.add_argument('-o', metavar='file',type=argparse.FileType('w'),default=sys.stdout)
  args = parser.parse_args()
  kml = main(args.i)
  kml.write(args.o)
