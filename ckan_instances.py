from __future__ import print_function
import urllib2
from urlparse import urlparse
import json

DATAPORTALS = 'http://dataportals.org/api/data.json'


def lookup_dataportals(dataportals):
    response = urllib2.urlopen(dataportals)
    data = json.load(response)

    ckan_portals = {}

    for portal_key in data:
        p = data[portal_key]
        if 'ckan' in p['generator'].lower() or 'ckan' in p['tags']:
            url = p['url']
            api_url = p['apiendpoint']

            if url:
                try:
                    # check if url exists
                    urllib2.urlopen(url)
                    parsed_uri = urlparse(url)
                    id = '{uri.netloc}'.format(uri=parsed_uri)
                    id = id.replace('.', '_')

                    api = 'not found'
                    if api_url:
                        try:
                            urllib2.urlopen(api_url)
                            api = api_url
                        except:
                            pass
                except urllib2.HTTPError, e:
                    print(e.code)
                except urllib2.URLError, e:
                    print(e.args)

                ckan_portals[id] = {'url': url, 'api': api}
    return ckan_portals

if __name__ == '__main__':
    p = lookup_dataportals(DATAPORTALS)

    for l in p:
        print(l)