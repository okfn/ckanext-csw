import os
from pkg_resources import resource_stream, resource_filename
from lxml import etree
log = __import__("logging").getLogger(__name__)

class BaseValidator(object):
    '''Base class for a validator.'''
    name = None
    title = None

    @classmethod
    def is_valid(cls, xml):
        '''
        Runs the validation on the supplied XML etree.
        Returns tuple:
          (is_valid, error_message_list)
        '''
        raise NotImplementedError

class SchematronValidator(BaseValidator):
    '''Base class for a validator that uses Schematron.'''
    has_init = False

    @classmethod
    def get_schematron(cls):
        raise NotImplementedError

    @classmethod
    def is_valid(cls, xml):
        if not hasattr(cls, 'schematrons'):
            log.info('Compiling "%s"', cls.title)
            cls.schematrons = cls.get_schematrons()
        for schematron in cls.schematrons:
            result = schematron(xml)
            errors = []
            for element in result.findall("{http://purl.oclc.org/dsdl/svrl}failed-assert"):
                errors.append(element)
            if len(errors) > 0:
                messages_already_reported = set()
                error_details = []
                for error in errors:
                    message, details = cls.extract_error_details(error)
                    if not message in messages_already_reported:
                        error_details.append(details)
                        messages_already_reported.add(message)
                return False, error_details
        return True, []

    @classmethod
    def extract_error_details(cls, failed_assert_element):
        '''Given the XML Element describing a schematron test failure,
        this method extracts the strings describing the failure and returns
        them.

        Returns:
           (error_message, fuller_error_details)
        '''
        assert_ = failed_assert_element.get('test')
        location = failed_assert_element.get('location')
        message_element = failed_assert_element.find("{http://purl.oclc.org/dsdl/svrl}text")
        message = message_element.text.strip()
        failed_assert_element
        return message, 'Error Message: "%s"  Error Location: "%s"  Error Assert: "%s"' % (message, location, assert_)

    @classmethod
    def schematron(cls, schema):
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

        
class ISO19139Schema(SchematronValidator):
    name = 'iso19139'
    title = 'ISO19139 XSD Schema'

    @classmethod
    def get_schematrons(cls):
        with resource_stream("ckanext.csw", "xml/schematron/ExtractSchFromXSD.xsl") as xsl_file:
            xsl = etree.parse(xsl_file)
            xsd2sch = etree.XSLT(xsl)

        root = resource_filename("ckanext.csw", "xml/iso19139")
        schematrons = []
        for filename in ["gmd/gmd.xsd"]:
            filename = os.path.join(root, filename)
            with open(filename) as xsd_file:
                xsd = etree.parse(xsd_file)
                schematrons.append(cls.schematron(xsd2sch(xsd)))
        return schematrons

class ConstraintsSchematron(SchematronValidator):
    name = 'constraints'
    title = 'ISO19139 Table A.1 Constraints Schematron 1.3'

    @classmethod
    def get_schematrons(cls):
        with resource_stream("ckanext.csw",
                             "xml/medin/ISOTS19139A1Constraints_v1.3.sch") as schema:
            return [cls.schematron(schema)]


class Gemini2Schematron(SchematronValidator):
    name = 'gemini2'
    title = 'GEMINI2 Schematron 1.2'

    @classmethod
    def get_schematrons(cls):
        with resource_stream("ckanext.csw",
                             "xml/gemini2/gemini2-schematron-20110906-v1.2.sch") as schema:
            return [cls.schematron(schema)]

all_validators = (ISO19139Schema,
                  ConstraintsSchematron,
                  Gemini2Schematron)


class Validator(object):
    '''
    Validates XML against one or more profiles (i.e. validators).
    '''
    def __init__(self, profiles=["iso19139", "constraints", "gemini2"]):
        self.profiles = profiles

    def isvalid(self, xml):
        '''For backward compatibility'''
        return is_valid(xml)
    
    def is_valid(self, xml):
        if not hasattr(self, 'validators'):
            self.validators = {} # name: class
            for validator_class in all_validators:
                self.validators[validator_class.name] = validator_class
        for name in self.profiles:
            validator = self.validators[name]
            is_valid, error_message_list = validator.is_valid(xml)
            if not is_valid:
                error_message_list.insert(0, 'Validating against "%s" profile failed' % validator.title)
                log.info('%r', error_message_list)
                return False, error_message_list
            log.info('Validated against "%s"', validator.title)
        log.info('Validation passed')
        return True, []
                
if __name__ == '__main__':
    from sys import argv
    import logging
    logging.basicConfig()
    
    v = Validators()
    v.is_valid(etree.parse(open(argv[1])))
