import argparse
from pprint import pprint
from ckanext.ows.services import CswService, WmsService

#remote = "http://www.nationaalgeoregister.nl/geonetwork/srv/eng/csw"
#remote = "http://locationmetadataeditor.data.gov.uk/geonetwork/srv/csw"

def owsinfo():
    """
    Hello World
    """
    parser = argparse.ArgumentParser(description=owsinfo.__doc__)

    parser.add_argument("-d", "--debug", dest="debug", action="store_true")
    
    sub = parser.add_subparsers()
    csw_p = sub.add_parser("csw", description=CswService.__doc__)
    csw_p.add_argument("operation", action="store", choices=CswService._operations())
    csw_p.add_argument("endpoint", action="store")
    csw_p.add_argument("ids", nargs="*")
    csw_p.add_argument("--qtype", help="type of resource to query (i.e. service, dataset)")
    csw_p.add_argument("--keywords", default=[], action="append",
                       help="list of keywords")
    csw_p.add_argument("--typenames", help="the typeNames to query against (default is csw:Record)")
                       
    csw_p.add_argument("--esn", help="the ElementSetName 'full', 'brief' or 'summary'")
    csw_p.add_argument("-s", "--skip", default=0, type=int)
    csw_p.add_argument("-c", "--count", default=10, type=int)
    csw_p.set_defaults(service=CswService)
    
    wms_p = sub.add_parser("wms", description=WmsService.__doc__)
    wms_p.add_argument("operation", action="store", choices=WmsService._operations())
    wms_p.add_argument("endpoint", action="store")
    wms_p.set_defaults(service=WmsService)

    args = parser.parse_args()
    service = args.service()
    value = service(args)
    if isinstance(value, basestring):
        print value
    elif value is not None:
        pprint(value)
