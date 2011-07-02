import gpxpy.tools
import datetime

def test_parse_timezone():
  assert gpxpy.tools.parse_timezone('America/Los_Angeles') is not None
  
def test_parse_timedelta():
  assert gpxpy.tools.parse_timedelta('12h') == datetime.timedelta(hours=12)