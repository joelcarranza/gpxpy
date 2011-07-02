import argparse
import sys
import gpxpy
from datetime import timedelta
import pytz
import re

def inoutargs():
  parser = argparse.ArgumentParser(add_help=False)
  # TODO: add help to these arguments
  parser.add_argument('-i', metavar='file',type=argparse.FileType('r'),default=sys.stdin)
  parser.add_argument('-o', metavar='file',type=argparse.FileType('w'),default=sys.stdout)
  # TODO: --name and --description tags for any writen out gpx files
  return parser
  
def gpxin(args):
  "Given arg setup using inoutargs - load the target GPX file"
  return gpxpy.parse(args.i)
  
def gpxout(gpx,args):
  "Given arg setup using inoutargs - write the target GPX file"
  gpx.write(args.o)
  
units_conv = dict(m=1.0,mi=1609.344,ft=0.3048,km=1000)

def parse_dist(str):
  """
  Parse a text distance of the form Nunits into meters
  >>> parse_dist('1m')
  1.0
  >>> parse_dist('5mi')
  8046.7200000000003
  >>> parse_dist('1500ft')
  457.20000000000005
  >>> parse_dist('1.1km')
  1100.0
  """
  m = re.match(r"(\d+(?:\.\d+)?)([a-zA-Z]+)?",str)
  if m:
    n = float(m.group(1))
    units = (m.group(2) or "m").lower()
    return n*units_conv[units]
  raise Exception("Failed to parse %s" %str)

def parse_timezone(tz):
  """
  Parse a timezone description into a tzinfo object
  >>> parse_timezone("America/Los Angeles")
  <DstTzInfo 'America/Los_Angeles' PST-1 day, 16:00:00 STD>
  >>> parse_timezone("America/Los_Angeles")
  <DstTzInfo 'America/Los_Angeles' PST-1 day, 16:00:00 STD>
  """
  return pytz.timezone(tz.replace(" ","_"))

def parse_timedelta(str):
  """
  Parse time string of the form Nunit into a datetime.timedelta 
  object
  
  >>> parse_timedelta('1h')
  datetime.timedelta(0, 3600)
  >>> parse_timedelta('1d')
  datetime.timedelta(1)
  >>> parse_timedelta('3d')
  datetime.timedelta(3)
  >>> parse_timedelta('60m')
  datetime.timedelta(0, 3600)
  """
  m = re.match(r"(\d+)([dhms])",str)
  if m:
    n = int(m.group(1))
    units = m.group(2)
    if units == 'd':
      return timedelta(days=n)
    if units == 'h':
      return timedelta(hours=n)
    if units == 'm':
      return timedelta(minutes=n)
    if units == 's':
      return timedelta(seconds=n)
  raise Exception("Failed to parse %s" %str)