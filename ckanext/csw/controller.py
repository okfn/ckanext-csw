try: from cStringIO import StringIO
except ImportError: from StringIO import StringIO
import traceback
from datetime import datetime
from pylons import request, response, config
from lxml import etree
from owslib.csw import namespaces
from sqlalchemy import select
from ckan.lib.base import BaseController
from ckan.model.meta import Session
from ckan.model.harvesting import HarvestedDocument

namespaces["xlink"] = "http://www.w3.org/1999/xlink"

log = __import__("logging").getLogger(__name__)

from random import random
class __rlog__(object):
    """
    Random log -- log wrapper to log a defined percentage
    of dialogues
    """
    def __init__(self, threshold=config["cswservice.rndlog_threshold"]):
        self.threshold = threshold
        self.i = random()
    def __getattr__(self, attr):
        if self.i > self.threshold:
            return self.dummy
        return getattr(log, attr)
    def dummy(self, *av, **kw):
        pass
       
def ntag(nselem):
    pfx, elem = nselem.split(":")
    return "{%s}%s" % (namespaces[pfx], elem)

class CatalogueServiceWebController(BaseController):

    def dispatch(self):
        self.rlog = __rlog__()
        self.rlog.info("request environ\n%s", request.environ)
        self.rlog.info("request headers\n%s", request.headers)
        self.rlog.info("request body\n%s", request.body)
        if request.method == "GET":
            if "request" not in request.GET:
                err = self.exception(exceptionCode="MissingParameterValue", location="request")
                return self.render_xml(err)
            if request.GET["request"] != "GetCapabilities":
                err = self.exception(exceptionCode="OperationNotSupported",
                            location=request.GET["request"])
                return self.render_xml(err)
            if "service" not in request.GET:
                err = self.exception(exceptionCode="MissingParameterValue", location="service")
                return self.render_xml(err)
            if request.GET["service"] != "CSW":
                err = self.exception(exceptionCode="InvalidParameterValue",
                            location=request.GET["service"])
                return self.render_xml(err)
            return self.get_capabilities()

        req = etree.parse(StringIO(request.body))
        root = req.getroot()
        if root.tag == "{http://www.opengis.net/cat/csw/2.0.2}GetCapabilities":
            return self.get_capabilities()
        if root.tag == "{http://www.opengis.net/cat/csw/2.0.2}GetRecordById":
            return self.get_record_by_id(root)
        if root.tag == "{http://www.opengis.net/cat/csw/2.0.2}GetRecords":
            return self.get_records(root)

        ### TODO: what is the proper exceptionCode??
        err = self.execption(exceptionCode="UnsupportedRequest")
        return self.render_xml(err)

    def render_xml(self, root):
        tree = etree.ElementTree(root)
        data = etree.tostring(tree, pretty_print=True)
        response.headers["Content-Length"] = len(data)
        response.content_type = "application/xml"
        response.charset="UTF-8"
        self.rlog.info("response headers:\n%s", response.headers)
        self.rlog.info("response.body:\n%s", data)
        return data

    def exception(self, **kw):
        metaargs = {
            "nsmap": namespaces,
            "version": "1.0.0",
            ntag("xsi:schemaLocation"): "http://schemas.opengis.net/ows/1.0.0/owsExceptionReport.xsd",
        }
        root = etree.Element(ntag("ows:ExceptionReport"), **metaargs)
        etree.SubElement(root, ntag("ows:Exception"), **kw)
        return root

    def get_capabilities(self):
        site = request.host_url + request.path        
        caps = etree.Element(ntag("csw:Capabilities"), nsmap=namespaces)
        srvid = etree.SubElement(caps, ntag("ows:ServiceIdentification"))
        title = etree.SubElement(srvid, ntag("ows:Title"))
        title.text = unicode(config["cswservice.title"])
        abstract = etree.SubElement(srvid, ntag("ows:Abstract"))
        abstract.text = unicode(config["cswservice.abstract"])
        keywords = etree.SubElement(srvid, ntag("ows:Keywords"))
        for word in [w.strip() for w in config["cswservice.keywords"].split(",")]:
            if word == "": continue
            kw = etree.SubElement(keywords, ntag("ows:Keyword"))
            kw.text = unicode(word)
        kwtype = etree.SubElement(keywords, ntag("ows:Type"))
        kwtype.text = unicode(config["cswservice.keyword_type"])
        srvtype = etree.SubElement(srvid, ntag("ows:ServiceType"))
        srvtype.text = "CSW"
        srvver = etree.SubElement(srvid, ntag("ows:ServiceTypeVersion"))
        srvver.text = "2.0.2"
        ### ows:Fees, ows:AccessConstraints

        provider = etree.SubElement(caps, ntag("ows:ServiceProvider"))
        provname = etree.SubElement(provider, ntag("ows:ProviderName"))
        provname.text = unicode(config["cswservice.provider_name"])
        attrs = {
            ntag("xlink:href"): site
            }
        etree.SubElement(provider, ntag("ows:ProviderSite"), **attrs)

        contact = etree.SubElement(caps, ntag("ows:ServiceContact"))
        name = etree.SubElement(contact, ntag("ows:IndividualName"))
        name.text = unicode(config["cswservice.contact_name"])
        pos = etree.SubElement(contact, ntag("ows:PositionName"))
        pos.text = unicode(config["cswservice.contact_position"])
        cinfo = etree.SubElement(contact, ntag("ows:ContactInfo"))
        phone = etree.SubElement(cinfo, ntag("ows:Phone"))
        voice = etree.SubElement(phone, ntag("ows:Voice"))
        voice.text = unicode(config["cswservice.contact_voice"])
        fax = etree.SubElement(phone, ntag("ows:Fax"))
        fax.text = unicode(config["cswservice.contact_fax"])
        addr = etree.SubElement(cinfo, ntag("ows:Address"))
        dpoint = etree.SubElement(addr, ntag("ows:DeliveryPoint"))
        dpoint.text= unicode(config["cswservice.contact_address"])
        city = etree.SubElement(addr, ntag("ows:City"))
        city.text = unicode(config["cswservice.contact_city"])
        region = etree.SubElement(addr, ntag("ows:AdministrativeArea"))
        region.text = unicode(config["cswservice.contact_region"])
        pcode = etree.SubElement(addr, ntag("ows:PostalCode"))
        pcode.text = unicode(config["cswservice.contact_pcode"])
        country = etree.SubElement(addr, ntag("ows:Country"))
        country.text = unicode(config["cswservice.contact_country"])
        email = etree.SubElement(addr, ntag("ows:ElectronicMailAddress"))
        email.text = unicode(config["cswservice.contact_email"])
        hours = etree.SubElement(cinfo, ntag("ows:HoursOfService"))
        hours.text = unicode(config["cswservice.contact_hours"])
        instructions = etree.SubElement(cinfo, ntag("ows:ContactInstructions"))
        instructions.text = unicode(config["cswservice.contact_instructions"])
        role = etree.SubElement(contact, ntag("ows:Role"))
        role.text = unicode(config["cswservice.contact_role"])

        opmeta = etree.SubElement(caps, ntag("ows:OperationsMetadata"))

        op = etree.SubElement(opmeta, ntag("ows:Operation"), name="GetCapabilities")
        dcp = etree.SubElement(op, ntag("ows:DCP"))
        http = etree.SubElement(dcp, ntag("ows:HTTP"))
        attrs = { ntag("xlink:href"): site }
        etree.SubElement(http, ntag("ows:Post"), **attrs)
        pe = etree.SubElement(op, ntag("ows:Constraint"), name="PostEncoding")
        val = etree.SubElement(pe, ntag("ows:Value"))
        val.text = "XML"

        op = etree.SubElement(opmeta, ntag("ows:Operation"), name="GetRecords")
        dcp = etree.SubElement(op, ntag("ows:DCP"))
        http = etree.SubElement(dcp, ntag("ows:HTTP"))
        attrs = { ntag("xlink:href"): site }
        etree.SubElement(http, ntag("ows:Post"), **attrs)
        pe = etree.SubElement(op, ntag("ows:Constraint"), name="PostEncoding")
        val = etree.SubElement(pe, ntag("ows:Value"))
        val.text = "XML"
        param = etree.SubElement(op, ntag("ows:Parameter"), name="resultType")
        val = etree.SubElement(param, ntag("ows:Value"))
        val.text = "results"
        param = etree.SubElement(op, ntag("ows:Parameter"), name="outputFormat")
        val = etree.SubElement(param, ntag("ows:Value"))
        val.text = "application/xml"
        param = etree.SubElement(op, ntag("ows:Parameter"), name="outputSchema")
        val = etree.SubElement(param, ntag("ows:Value"))
        val.text = "http://www.isotc211.org/2005/gmd"
        param = etree.SubElement(op, ntag("ows:Parameter"), name="typeNames")
        val = etree.SubElement(param, ntag("ows:Value"))
        val.text = "gmd:MD_Metadata"

        op = etree.SubElement(opmeta, ntag("ows:Operation"), name="GetRecordById")
        dcp = etree.SubElement(op, ntag("ows:DCP"))
        http = etree.SubElement(dcp, ntag("ows:HTTP"))
        attrs = { ntag("xlink:href"): site }
        etree.SubElement(http, ntag("ows:Post"), **attrs)
        pe = etree.SubElement(op, ntag("ows:Constraint"), name="PostEncoding")
        val = etree.SubElement(pe, ntag("ows:Value"))
        val.text = "XML"
        param = etree.SubElement(op, ntag("ows:Parameter"), name="resultType")
        val = etree.SubElement(param, ntag("ows:Value"))
        val.text = "results"
        param = etree.SubElement(op, ntag("ows:Parameter"), name="outputFormat")
        val = etree.SubElement(param, ntag("ows:Value"))
        val.text = "application/xml"
        param = etree.SubElement(op, ntag("ows:Parameter"), name="outputSchema")
        val = etree.SubElement(param, ntag("ows:Value"))
        val.text = "http://www.isotc211.org/2005/gmd"
        param = etree.SubElement(op, ntag("ows:Parameter"), name="typeNames")
        val = etree.SubElement(param, ntag("ows:Value"))
        val.text = "gmd:MD_Metadata"

        filcap = etree.SubElement(caps, ntag("ogc:Filter_Capabilities"))
        spacap = etree.SubElement(filcap, ntag("ogc:Spatial_Capabilities"))
        geomop = etree.SubElement(spacap, ntag("ogc:GeometryOperands"))
        spaceop = etree.SubElement(spacap, ntag("ogc:SpatialOperators"))

        scalcap = etree.SubElement(filcap, ntag("ogc:Scalar_Capabilities"))
        lop = etree.SubElement(scalcap, ntag("ogc:LogicalOperators"))
        cop = etree.SubElement(scalcap, ntag("ogc:ComparisonOperators"))

        idcap = etree.SubElement(filcap, ntag("ogc:Id_Capabilities"))
        eid = etree.SubElement(idcap, ntag("ogc:EID"))
        fid = etree.SubElement(idcap, ntag("ogc:FID"))
        
        return self.render_xml(caps)
        
    def _parse_request_common(self, root):
        """
        Check common parts of the request for GetRecords, GetRecordById, etc.
        Return a dictionary of parameters or else an XML error message (string)
        """
        service = root.get("service")
        if service is None:
            err = self.exception(exceptionCode="MissingParameterValue", location="service")
            return self.render_xml(err)
        elif service != "CSW":
            err = self.exception(exceptionCode="InvalidParameterValue", location="service")
            return self.render_xml(err)
        outputSchema = root.get("outputSchema", namespaces["gmd"])
        if outputSchema != namespaces["gmd"]:
            err = self.exception(exceptionCode="InvalidParameterValue", location="outputSchema")
            return self.render_xml(err)
        resultType = root.get("resultType", "results")
        if resultType != "results":
            err = self.exception(exceptionCode="InvalidParameterValue", location="resultType")
            return self.render_xml(err)
        outputFormat = root.get("outputFormat", "application/xml")
        if outputFormat != "application/xml":
            err = self.exception(exceptionCode="InvalidParameterValue", location="outputFormat")
            return self.render_xml(err)
        elementSetName = root.get("elementSetName", "full")
        if elementSetName not in ("full", "brief"):
            err = self.exception(exceptionCode="InvalidParameterValue", location="elementSetName")
            return self.render_xml(err)

        params = {
            "outputSchema": outputSchema,
            "resultType": resultType,
            "outputFormat": outputFormat,
            "elementSetName": elementSetName
            }
        return params
    
    def get_records(self, root):
        req = self._parse_request_common(root)
        if not isinstance(req, dict):
            return req
        
        startPosition = root.get("startPosition", "0")
        try:
            startPosition = int(startPosition)
        except:
            err = self.exception(exceptionCode="InvalidParameterValue", location="startPosition")
            return self.render_xml(err)
        maxRecords = root.get("maxRecords", "0")
        try:
            maxRecords = int(maxRecords)
        except:
            err = self.exception(exceptionCode="InvalidParameterValue", location="maxRecords")
            return self.render_xml(err)

        resp = etree.Element(ntag("csw:GetRecordsResponse"), nsmap=namespaces)
        etree.SubElement(resp, ntag("csw:SearchStatus"), timestamp=datetime.utcnow().isoformat())

        cursor = Session.connection()
        
        #q = Session.query(HarvestedDocument).order_by(HarvestedDocument.created.desc())
        q  = select([HarvestedDocument.guid]
                    ).order_by(HarvestedDocument.created.desc()
                               )
        ### TODO Parse query instead of stupidly just returning whatever we like
        rset = q.offset(startPosition).limit(maxRecords)

        total = Session.execute(q.alias().count()).first()[0]
        returned = Session.execute(rset.alias().count()).first()[0]
        attrs = {
            "numberOfRecordsMatched": total,
            "numberOfRecordsReturned": returned,
            "elementSet": "full"
            }
        if attrs["numberOfRecordsMatched"] > attrs["numberOfRecordsReturned"]:
            attrs["nextRecord"]  = attrs["numberOfRecordsReturned"] + 1
        attrs = dict((k, unicode(v)) for k,v in attrs.items())
        results = etree.SubElement(resp, ntag("csw:SearchResults"), **attrs)
                                                          
        for guid, in Session.execute(rset):
            doc = Session.query(HarvestedDocument
                                ).filter(HarvestedDocument.guid==guid
                                         ).order_by(HarvestedDocument.created.desc()
                                                    ).limit(1).first()
            try:
                record = etree.parse(StringIO(doc.content.encode("utf-8")))
                results.append(record.getroot())
            except:
                log.error("exception parsing document %s:\n%s", doc.id, traceback.format_exc())
                raise
            
        return self.render_xml(resp)

    def get_record_by_id(self, root):
        req = self._parse_request_common(root)
        if not isinstance(req, dict):
            return req

        resp = etree.Element(ntag("csw:GetRecordByIdResponse"), nsmap=namespaces)
        seen = set()
        for ident in root.findall(ntag("csw:Id")):
            doc = Session.query(HarvestedDocument
                                ).filter(HarvestedDocument.guid==ident.text,
                                         ).order_by(HarvestedDocument.created.desc()
                                                    ).limit(1).first()
            if doc is None:
                continue
            try:
                record = etree.parse(StringIO(doc.content.encode("utf-8")))
                resp.append(record.getroot())
            except:
                log.error("exception parsing document %s:\n%s", doc.id, traceback.format_exc())
                raise

        return self.render_xml(resp)
