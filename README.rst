===========
ckanext-csw
===========

ckanext-csw is:
 * a basic CSW server - to server metadata from the CKAN instance
 * a command-line tool to help making requests of any CSW server

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


Setup
=====

Install this extension into your python environment using as usual::

  pip install -e git+https://github.com/okfn/ckanext-csw#egg=ckanext-csw

This extension requires that ckanext-harvest is also installed - see https://github.com/okfn/ckanext-harvest

Currently the library dependencies aren't setup to install automatically, so do this::

  pip install owslib 'lxml<=2.2.99' argparse

Enable the extension by adding ``cswserver`` to your ckan.plugins line in your CKAN config file (``harvest`` should be there already from the ckanext-harvest install)::

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

cswservice.rndlog_threshold is the percentage of interactions to store in the log file.