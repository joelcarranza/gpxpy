import xml.etree.cElementTree as ET
import functools

"""
KmlFactory

creates KML elements in a nice way
"""

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
KmlFactory = _K()