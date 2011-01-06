"""
Some very thin wrapper classes around those in OWSLib
for convenience.
"""

class OwsService(object):
    def __init__(self, endpoint=None):
        if endpoint is not None:
            self._ows(endpoint)
            
    def __call__(self, args):
        return getattr(self, args.operation)(**self._xmd(args))
    
    @classmethod
    def _operations(cls):
        return [x for x in dir(cls) if not x.startswith("_")]
    
    def _xmd(self, obj):
        md = {}
        for attr in [x for x in dir(obj) if not x.startswith("_")]:
            val = getattr(obj, attr)
            if not val:
                pass
            elif callable(val):
                pass
            elif isinstance(val, basestring):
                md[attr] = val
            elif isinstance(val, int):
                md[attr] = val
            elif isinstance(val, list):
                md[attr] = val
            else:
                md[attr] = self._xmd(val)
        return md
        
    def _ows(self, endpoint=None, **kw):
        if not hasattr(self, "_Implementation"):
            raise NotImplementedError("Needs an Implementation")
        if not hasattr(self, "__ows_obj__"):
            if endpoint is None:
                raise ValueError("Must specify a service endpoint")
            self.__ows_obj__ = self._Implementation(endpoint)
        return self.__ows_obj__
    
    def getcapabilities(self, debug=False, **kw):
        ows = self._ows(**kw)
        caps = self._xmd(ows)
        if not debug:
            if "request" in caps: del caps["request"]
            if "response" in caps: del caps["response"]
        if "owscommon" in caps: del caps["owscommon"]
        return caps
    
class CswService(OwsService):
    """
    Perform various operations on a CSW service
    """
    from owslib.csw import CatalogueServiceWeb as _Implementation
    def getrecords(self, qtype="service", keywords=[],
                   typenames="csw:Record", esn="brief",
                   skip=0, count=10, **kw):
        csw = self._ows(**kw)
        kwa = {
            "qtype": qtype,
            "keywords": keywords,
            "typenames": typenames,
            "esn": esn,
            "startposition": skip,
            "maxrecords": count,
            }
        csw.getrecords(**kwa)
        return [self._xmd(r) for r in csw.records.values()]

    def getrecordbyid(self, ids=[], esn="full", outputschema="gmd", **kw):
        from owslib.csw import namespaces
        csw = self._ows(**kw)
        kwa = {
            "esn": esn,
            "outputschema": namespaces[outputschema],
            }
        csw.getrecordbyid(ids, **kwa)
        return [self._xmd(r) for r in csw.records.values()]
        
class WmsService(OwsService):
    """
    Perform various operations on a WMS service
    """
    from owslib.wms import WebMapService as _Implementation
