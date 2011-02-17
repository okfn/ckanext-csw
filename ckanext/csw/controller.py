try: from cStringIO import StringIO
except ImportError: from StringIO import StringIO
from pylons import request, response, config
from lxml import etree
from owslib.csw import namespaces
from ckan.lib.base import BaseController

namespaces["xlink"] = "http://www.w3.org/1999/xlink"

def ntag(nselem):
    pfx, elem = nselem.split(":")
    return "{%s}%s" % (namespaces[pfx], elem)

class CatalogueServiceWebController(BaseController):
    def dispatch(self):
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
        
        print etree.tostring(req, pretty_print=True)
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
        print data
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
        
    def get_records(self, root):
        err = self.exception(exceptionCode="help")
        return self.render_xml(err)

    def get_record_by_id(self, root):
        err = self.exception(exceptionCode="help")
        return self.render_xml(err)
        
