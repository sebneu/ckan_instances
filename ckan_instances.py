from __future__ import print_function
import urllib2
from urlparse import urlparse
import json
import csv

DATAPORTALS = 'http://dataportals.org/api/data.json'


def get_id_from_url(url):
    parsed_uri = urlparse(url)
    id = '{uri.netloc}'.format(uri=parsed_uri)
    return id.replace('.', '_')


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

                    # get id
                    id = get_id_from_url(url)

                    api = None
                    if api_url:
                        try:
                            urllib2.urlopen(api_url)
                            api = api_url
                        except:
                            print(id+': api error')
                    ckan_portals[id] = {'url': url, 'api': api}
                except urllib2.HTTPError, e:
                    print(e.code)
                except urllib2.URLError, e:
                    print(e.args)
    return ckan_portals


def read_csv(file_obj):
    csvf = csv.reader(file_obj)
    ckan_portals = {}

    # my portals are stored in 2 columns, url and api
    for row in csvf:
        url = row[0]
        api = row[1]

        id = get_id_from_url(url)
        if api == 'not found':
            api = None

        ckan_portals[id] = {'url': url, 'api': api}
    return ckan_portals

if __name__ == '__main__':
    with open('instances.csv') as f:
        csvlist = read_csv(f)

    p = lookup_dataportals(DATAPORTALS)

    for key in p:
        if key not in csvlist:
            print(key + ' ' + str(p[key]['api']))
