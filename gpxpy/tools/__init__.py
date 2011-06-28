import argparse
import sys
import gpxpy
from datetime import timedelta
import pytz
import re

def inoutargs():
  parser = argparse.ArgumentParser(add_help=False)
  # TODO: add help to these areguments
  parser.add_argument('-i', metavar='file',type=argparse.FileType('r'),default=sys.stdin)
  parser.add_argument('-o', metavar='file',type=argparse.FileType('w'),default=sys.stdout)
  # TODO: --name and --description tags for any writen out gpx files
  return parser
  
def gpxin(args):
  return gpxpy.parse(args.i)
  
def gpxout(gpx,args):
  # TODO: ammend with name and description tags
  gpx.write(args.o)
  
def parse_timezone(str):
  # TODO: replace spaces with underscores for more lax parsing
  return pytz.timezone(str)

def parse_timedelta(str):
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