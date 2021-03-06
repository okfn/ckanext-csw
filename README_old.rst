===========
ckanext-csw
===========

.. warning::
   This module is DEPRECATED as of 19/10/12. It has been merged into https://github.com/okfn/ckanext-spatial

ckanext-csw is made of several distinct parts:
 * CSW Server - a basic CSW server - to serve metadata from the CKAN instance
 * CSW Client - a basic client for accessing a CSW server
 * cswinfo - a command-line tool to help making requests of any CSW server
 * Validator - a python library that uses Schematron to validate geographic metadata XML

CSW (Catalogue Service for the Web) is an OGC standard for a web interface that allows you to access metadata (which are records that describe data or services)

CSW Server
==========

The currently supported methods with this CSW Server are:
 * GetCapabilities
 * GetRecords
 * GetRecordById

ckanext-csw provides the CSW service at ``/csw``. 

For example you can ask the capabilities of the CSW server installed into CKAN running on 127.0.0.1:5000 like this::

 curl 'http://127.0.0.1:5000/csw?request=GetCapabilities&service=CSW'

The standard CSW response is in XML format.

CSW Client
==========

CswService is a client for python software (such as the CSW Harvester in ckanext-inspire) to conveniently access a CSW server, using the same three methods as the CSW Server supports. It is a wrapper around OWSLib's tool, dealing with the details of the calls and responses to make it very convenient to use, whereas OWSLib on its own is more complicated.

cswinfo tool
============

When ckanext-csw is installed, it provides a command-line tool ``cswinfo``, for making queries on CSW servers and returns the info in nicely formatted JSON. This may be more convenient to type than using, for example, curl.

Currently available queries are: 
 * getcapabilities
 * getidentifiers
 * getrecords
 * getrecordbyid

For details, type::

 cswinfo csw -h

There are options for querying by only certain types, keywords and typenames as well as configuring the ElementSetName.

The equivalent example to the one above for asking the cabailities is::

 $ cswinfo csw getcapabilities http://127.0.0.1:5000/csw

OWSLib is the library used to actually perform the queries.

Validator
=========

This python library uses Schematron and other schemas to validate the XML.

Here is a simple example of using the Validator library:

 from ckanext.csw.validation import Validator
 xml = etree.fromstring(gemini_string)
 validator = Validator(profiles=('iso19139', 'gemini2', 'constraints'))
 valid, messages = validator.isvalid(xml)
 if not valid:
     print "Validation error: " + messages[0] + ':\n' + '\n'.join(messages[1:])

In DGU, the Validator is integrated here:
https://github.com/okfn/ckanext-inspire/blob/master/ckanext/inspire/harvesters.py#L88

NOTE: The ISO19139 XSD Validator requires system library ``libxml2`` v2.9 (released Sept 2012). If you intend to use this validator then see the section below about installing libxml2.

Setup
=====

Install this extension into your python environment using as usual::

  pip install -e git+https://github.com/okfn/ckanext-csw#egg=ckanext-csw

This extension requires that ckanext-harvest is also installed - see https://github.com/okfn/ckanext-harvest

Currently the library dependencies aren't setup to install automatically, so do this::

  pip install owslib 'lxml<=2.2.99' argparse

To enable the CSW Server you should adding ``cswserver`` to your ckan.plugins line in your CKAN config file (``harvest`` should be there already from the ckanext-harvest install)::

  ckan.plugins = harvest cswserver

Configure the extension itself with the following keys in your CKAN config file (default values are shown)::

  cswservice.title = Untitled Service - set cswservice.title in config
  cswservice.abstract = Unspecified service description - set cswservice.abstract in config
  cswservice.keywords = 
  cswservice.keyword_type = theme
  cswservice.provider_name = Unnamed provider - set cswservice.provider_name in config
  cswservice.contact_name = No contact - set cswservice.contact_name in config
  cswservice.contact_position = 
  cswservice.contact_voice = 
  cswservice.contact_fax = 
  cswservice.contact_address = 
  cswservice.contact_city = 
  cswservice.contact_region = 
  cswservice.contact_pcode = 
  cswservice.contact_country = 
  cswservice.contact_email = 
  cswservice.contact_hours = 
  cswservice.contact_instructions = 
  cswservice.contact_role = 
  cswservice.rndlog_threshold = 0.01
  cswservice.log_xml_length = 1000

cswservice.rndlog_threshold is the percentage of interactions to store in the log file.

Installing libxml2
==================

Version 2.9 is required for the ISO19139 XSD validation.

With CKAN you would probably have installed an older version from your distribution. (e.g. with ``sudo apt-get install libxml2-dev``). You need to find the SO files for the old version::

  $ find /usr -name "libxml2.so"

For example, it may show it here: ``/usr/lib/x86_64-linux-gnu/libxml2.so``. The directory of the SO file is used as a parameter to the ``configure`` next on.

Download the libxml2 source::

  $ cd ~
  $ wget ftp://xmlsoft.org/libxml2/libxml2-2.9.0.tar.gz

Unzip it::

  $ tar zxvf libxml2-2.9.0.tar.gz
  $ cd libxml2-2.9.0/

Configure with the SO directory you found before::

  $ ./configure --libdir=/usr/lib/x86_64-linux-gnu

Now make it and install it::

  $ make
  $ sudo make install

Now check the install by running xmllint::

  $ xmllint --version
  xmllint: using libxml version 20900
     compiled with: Threads Tree Output Push Reader Patterns Writer SAXv1 FTP HTTP DTDValid HTML Legacy C14N Catalog XPath XPointer XInclude Iconv ISO8859X Unicode Regexps Automata Expr Schemas Schematron Modules Debug Zlib 
