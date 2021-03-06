import argparse
import urllib2
import httplib
from urlparse import urlparse
import json
import csv
import sys

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


def lookup_revision(api_url):
    try:
        url = api_url.split('/api')[-2] + '/revision/list?format=atom'
        if check_url(url):
            return url
    except:
        print('Feed error: ' + url)
        pass
    return ''


def check_url(url):
    p = urlparse(url)
    conn = httplib.HTTPConnection(p.netloc)
    conn.request('HEAD', p.path)
    resp = conn.getresponse()
    return resp.status < 400


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
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('--revision', help='run revision list check', action='store_true')
    parser.add_argument('--dataportals', help='run dataportals check', action='store_true')
    args = parser.parse_args()

    # read file
    with open(filename+'.csv', 'r') as f:
        csvlist = read_csv(f)
    print(str(len(csvlist)) + ' items in CSV list')

    if args.dataportals:
        # get dataportals URLs
        p = lookup_dataportals(DATAPORTALS)
        print(str(len(p)) + ' CKAN instances in dataportals.org')

        csvlist = join_list(csvlist, p)
        print(str(len(csvlist)) + ' items in joined list')

        # rewrite file
        with open(filename+'.csv', 'wb') as f:
            write_csv(f, csvlist)

    if args.revision:
        # look for revision atom feed
        revision_feed = []
        for key in csvlist:
            if csvlist[key]['api']:
                rev = lookup_revision(csvlist[key]['api'])
                revision_feed.append([csvlist[key]['api'], rev])
                csvlist[key]['revision'] = rev
        with open('revision_feed.csv', 'wb') as h:
            csvw = csv.writer(h)
            csvw.writerow(['url', 'revision_feed'])
            csvw.writerows(revision_feed)

    # rewrite json file
    with open(filename+'.json', 'wb') as f:
        json.dump(csvlist, f)
