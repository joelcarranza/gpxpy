import gpxpy
import os.path
import os

def load(name):
  "Read a gpx file by name from tests directory"
  test_dir = os.path.dirname(__file__)
  fn = os.path.join(test_dir,name)
  return gpxpy.parse(open(fn,'r'))
  
  
def test_load():
  test_dir = os.path.dirname(__file__)
  for fn in os.listdir(test_dir):
    basename,ext = os.path.splitext(fn)
    if ext == '.gpx':
      load(fn)
