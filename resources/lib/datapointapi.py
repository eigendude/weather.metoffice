#API for the Met Office's DataPoint API
#http://www.metoffice.gov.uk/datapoint
import urllib
import urllib2
from utilities import retryurlopen

#resource can be 'wxobs', 'wxfcs'
#format can be 'val', 'txt', 'image', 'layer'
#datatype can be 'json', 'xml'
#object can be 'sitelist', 'capabilties', \d+ (string of digits)
BASE_URL = "http://datapoint.metoffice.gov.uk/public/data/"
RESOURCE_URL = "%(format)s/%(resource)s/%(group)s/%(datatype)s/%(object)s?%(params)s"

SITELIST_TYPES = ['ForecastLocation', 'ObservationLocation', 'RegionalLocation']

LONG_REGIONAL_NAMES = {'os': 'Orkney and Shetland',
                       'he': 'Highland and Eilean Siar',
                       'gr': 'Grampian',
                       'ta': 'Tayside',
                       'st': 'Strathclyde',
                       'dg': 'Dumfries, Galloway, Lothian',
                       'ni': 'Northern Ireland',
                       'yh': 'Yorkshire and the Humber',
                       'ne': 'Northeast England',
                       'em': 'East Midlands',
                       'ee': 'East of England',
                       'se': 'London and Southeast England',
                       'nw': 'Northwest England',
                       'wm': 'West Midlands',
                       'sw': 'Southwest England',
                       'wl': 'Wales',
                       'uk': 'United Kingdom'}

def clean_sitelist(sitelist):
    """
    A bug in datapoint returns keys prefixed with '@'
    This func chops them out
    """
    new_sites = []
    new_site = {}

    for site in sitelist:
        for key in site:
           if key.startswith('@'):
               new_key = key[1:]
               new_site[new_key] = site[key]
        new_sites.append(new_site.copy())
    return new_sites

def filter_sitelist(text, sitelist):
    """
    Takes a list of dictionaries and returns only
    those entries whose 'name' key contains text
    """
    filteredsitelist = list()
    for x in sitelist:
        if x['name'].lower().find(text.lower()) != -1:
            filteredsitelist.append(x)
    return filteredsitelist

#get data from datapoint
def url(format='val', resource='wxobs', group='all', datatype='json', object='sitelist', params={}):
    #todo: validate parameters
    get_params = urllib.urlencode(params)
    substitute = {'format': format,
                  'resource': resource,
                  'group': group,
                  'datatype': datatype,
                  'object': object,
                  'params': get_params}
    return BASE_URL + RESOURCE_URL % substitute