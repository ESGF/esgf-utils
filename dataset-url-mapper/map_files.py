import requests, json
from urlparse import urlparse

# Load this table from a .json file
sample_table = { 'esg_dataroot' : '/path/to/data',
		 '/cmip5_css02_data': '/path/to/cmip5_02/data',
		 '/cmip5_css01_data': '/path/to/cmip5_01/data',
		  'css03_data': '/path/to/css03/data', 'user_pub_work': '/path/to/user/data' }



def get_mapped_dataset(id):

	search_url = "https://esgf-node.llnl.gov/esg-search/search/?type=File&dataset_id={}&format=application%2fsolr%2bjson".format(id)

	resp = requests.get(search_url)

	docs = json.loads(resp.text)["response"]["docs"]

	urllst = [x['url'][0] for x in docs]

	return urllst


def parse_and_map(url, table):

	strparts = url.split('|')
	res = urlparse(strparts[0])

	thepath = res.path
	pathparts = thepath.split('/')

	# Entry at index 3 is the logical thredds dataroot that needs to be mapped
	mappedroot = table[pathparts[3]]

	return '/'.join([mappedroot] + pathparts[4:])


def map_datasets(id):

	for url in get_mapped_dataset(id):

		print parse_and_map(url, sample_table)


import sys

# test example files:
#  'cmip5.output1.CMCC.CMCC-CM.historical.day.atmos.day.r1i1p1.v20120514|aims3.llnl.gov'
# 'CMIP6.CMIP.NASA-GISS.GISS-E2-1-G.historical.r1i1p1f1.3hr.clt.gn.v20181015|aims3.llnl.gov'

map_datasets(sys.argv[1])

