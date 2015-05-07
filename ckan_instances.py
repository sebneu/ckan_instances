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
                            print('API error: ' + id)
                    ckan_portals[id] = {'url': url, 'api': api}
                except urllib2.HTTPError, e:
                    print('URL error: ' + url + ', ' + str(e.code))
                except urllib2.URLError, e:
                    print('URL error: ' + url + ', ' + str(e.args))
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


def write_csv(f, joined):
    tuples = []
    for key in joined:
        tuples.append([joined[key]['url'], joined[key]['api']])
    sorted_tuples = sorted(tuples, key=lambda tup: tup[0])
    csvw = csv.writer(f)
    csvw.writerows(sorted_tuples)


def join_list(csvlist, dataportal):
    # at first collect all ids from dataportal.org not in the csv list
    new_portals = {}
    for key in dataportal:
        if key not in csvlist:
            print('Not in CSV list: ' + key + ' ' + str(p[key]['api']))
            new_portals[key] = p[key]
    # TODO look for APIs in dataportal which are not in the csv list
    joined = csvlist.copy()
    joined.update(new_portals)
    return joined


if __name__ == '__main__':
    filename = 'instances'

    # read file
    with open(filename+'.csv', 'r') as f:
        csvlist = read_csv(f)
    print(str(len(csvlist)) + ' items in CSV list')

    p = lookup_dataportals(DATAPORTALS)
    print(str(len(p)) + ' CKAN instances in dataportals.org')

    joined = join_list(csvlist, p)
    print(str(len(joined)) + ' items in joined list')

    # rewrite file
    with open(filename+'.csv', 'wb') as f:
        write_csv(f, joined)

    # rewrite file
    with open(filename+'.json', 'wb') as f:
        json.dump(joined, f)