import os
from pkg_resources import resource_stream, resource_filename
from lxml import etree
log = __import__("logging").getLogger(__name__)

__ns__ = {
    "svrl": "http://purl.oclc.org/dsdl/svrl",
    }

def schematron(schema):
    transforms = [
        "xml/schematron/iso_dsdl_include.xsl",
        "xml/schematron/iso_abstract_expand.xsl",
        "xml/schematron/iso_svrl_for_xslt1.xsl",
        ]
    if isinstance(schema, file):
        compiled = etree.parse(schema)
    else:
        compiled = schema
    for filename in transforms:
        with resource_stream("ckanext.csw", filename) as stream:
            xform_xml = etree.parse(stream)
            xform = etree.XSLT(xform_xml)
            compiled = xform(compiled)
    return etree.XSLT(compiled)

def isoconstraints_schematron():
    with resource_stream("ckanext.csw",
                         "xml/medin/ISOTS19139A1Constraints_v1.3.sch") as schema:
        return schematron(schema)

def gemini2_schematron():
    with resource_stream("ckanext.csw",
                         "xml/gemini2/gemini2-schematron-20101014-v1.0.sch") as schema:
        return schematron(schema)

def iso19139_schematrons():
    with resource_stream("ckanext.csw", "xml/schematron/ExtractSchFromXSD.xsl") as xsl_file:
        xsl = etree.parse(xsl_file)
        xsd2sch = etree.XSLT(xsl)

    root = resource_filename("ckanext.csw", "xml/iso19139")
    for filename in ["gmd/gmd.xsd"]:
        filename = os.path.join(root, filename)
        with open(filename) as xsd_file:
            xsd = etree.parse(xsd_file)
            yield schematron(xsd2sch(xsd))

class Validator(object):
    def __init__(self, profiles=["iso19139", "constraints", "gemini2"]):
        log.info("Initialising...")
        self.profiles = profiles
        self.schematrons = {}
        if "iso19139" in profiles:
            log.info("Compiling iso19139 schematron")
            self.schematrons["iso19139"] = list(iso19139_schematrons())
        if "constraints" in profiles:
            log.info("Compiling iso19139 constraints schematron")
            self.schematrons["constraints"] = [isoconstraints_schematron()]
        if "gemini2" in profiles:
            log.info("Compiling GEMINI 2 schematron")
            self.schematrons["gemini2"] = [gemini2_schematron()]

    def isvalid(self, xml):
        for name in self.profiles:
            for schematron in self.schematrons[name]:
                result = schematron(xml)
                errors = []
                for element in result.findall("{http://purl.oclc.org/dsdl/svrl}failed-assert"):
                    errors.append(element)
                if len(errors) > 0:
                    messages = []
                    for error in errors:
                        errtext = error.find("{http://purl.oclc.org/dsdl/svrl}text")
                        message = errtext.text.strip()
                        if not message in messages:
                            messages.append(message)
                    messages = ["Validating against %s profile failed" % name] + \
                        list(set(messages))
                    return False, messages
        return True, []
                
if __name__ == '__main__':
    from sys import argv
    import logging
    logging.basicConfig()
    
    v = Validator()
    v.isvalid(etree.parse(open(argv[1])))
