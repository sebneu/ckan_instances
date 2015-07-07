import csv
import json
import urllib2
from ckan_instances import read_csv

__author__ = 'sebastian'


if __name__ == '__main__':
    filename = 'instances'

    with open(filename+'.csv', 'r') as f:
        csvlist = read_csv(f)

    for id in csvlist:
        if csvlist[id]['api']:
            try:
                ds_list_url = csvlist[id]['api'] + '/rest/dataset'
                response = urllib2.urlopen(ds_list_url)
                data = json.load(response)
                if isinstance(data, list):
                    csvlist[id]['ds_list'] = len(data)
            except Exception, e:
                print id, 'No ds list accessible'
                print e

            try:
                full_list_url = csvlist[id]['api'] + '/action/package_search'
                response = urllib2.urlopen(full_list_url)
                data = json.load(response)
                if data['success'] and 'result' in data:
                    csvlist[id]['full_list'] = len(data['result'])
            except Exception, e:
                print id, 'No full list accessible'
                print e

    with open('full_ds_list.csv', 'w') as f:
        f.write('url,ds list,full list\n')
        for id in csvlist:
            line = [csvlist[id]['url'], str(csvlist[id].get('ds_list', '')), str(csvlist[id].get('full_list', ''))]
            f.write(','.join(line) + '\n')
