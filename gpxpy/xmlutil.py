#!/usr/bin/env python
# encoding: utf-8
"""
xmlutil.py

Some simple utilities for working with xml

Created by Joel Carranza on 2011-06-12.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

from xml.etree.cElementTree import Element
import pytz
# this is going to fail on 2.5???
import isodate

# Taken from: http://infix.se/2007/02/06/gentlemen-indent-your-xml
def indent(elem, level=0):
  "Indents an ElementTree"
  i = "\n" + level*"  "
  if len(elem):
      if not elem.text or not elem.text.strip():
          elem.text = i + "  "
      for e in elem:
          indent(e, level+1)
          if not e.tail or not e.tail.strip():
              e.tail = i + "  "
      if not e.tail or not e.tail.strip():
          e.tail = i
  else:
      if level and (not elem.tail or not elem.tail.strip()):
          elem.tail = i

class XAttr(object):
  """Really simple model for dealing with xml"""
  def __init__(self, name,elname=None,type='s',attr=False):
    self.name = name
    self.elname = elname if elname else name
    self.type = type
    self.attr = attr
    
  def tostr(self,value):
    if self.type == 'd':
      text = isodate.datetime_isoformat(value.astimezone(pytz.utc))
    else:
      text = str(value)
    return text
    
  def fromstr(self,text):
    type = self.type
    if type == 's':
      value = text
    elif type == 'd':
      value = isodate.parse_datetime(text).astimezone(pytz.utc)
    elif type == 'i':
      value = int(text)
    elif type == 'n':
      value = float(text)
    else:
      raise Error("Unknown format")
    return value
    
def init(self,values,attrs):
  for attr in attrs:
    if attr.name in values:
      setattr(self,attr.name,values[attr.name])
    else:
      setattr(self,attr.name,None)

def parse(ns,el,attrs):
  "parse from XML element to construct model"
  model = dict()
  for attr in attrs:
    value = None
    text = None
    if attr.attr:
      text = el.attrib[attr.elname]
    else:
      child = el.find("{%s}%s" % (ns,attr.elname))
      if child is not None:
        text = child.text
    if text:
      model[attr.name] = attr.fromstr(text)
  return model
  
def write(el,model,attrs):
  "construct element representing model from attributes"
  for attr in attrs:
    value = getattr(model,attr.name)
    if value is not None:
      text = attr.tostr(value)
      if attr.attr:
        el.attrib[attr.elname] = text
      else:
        c = Element(attr.elname)
        c.text = text
        el.append(c)
