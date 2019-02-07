import requests, json
from urlparse import urlparse

# Load this table from a .json file
table = { 'esg_dataroot' : '/path/to/data' }



def get_mapped_dataset(id):

	search_url = "https://esgf-node.llnl.gov/esg-search/search/?type=File&dataset_id={}&format=application%2fsolr%2bjson".format(id)

	resp = requests.get(search_url)

	docs = json.loads(resp.text)["response"]["docs"]

	urllst = [x['url'][0] for x in docs]

	return urllst


def parse_and_map(url):

	strparts = url.split('|')
	res = urlparse(strparts[0])

	thepath = res.path
	pathparts = thepath.split('/')

	# Entry at index 3 is the logical thredds dataroot that needs to be mapped
	mappedroot = table[pathparts[3]]

	return '/'.join([mappedroot] + pathparts[4:])


def map_datasets(id):

	for url in get_mapped_dataset(id):

		print parse_and_map(url)


import sys

map_datasets(sys.argv[1])



