import requests
import json
import datetime
import argparse
import collections


def build_table(holdings, source_id_list, col_names, time_shade=False):

	GRAY = "CCCCCC"
	MISSING = ""

	header_cell = "<th>{}</th>"
	row_cell_b="<tr><td><b>{}</b></td>"
	cell = '<td bgcolor="#{}">{}</td>'

	# If time_shade is enabled, then the cells will be shaded by how recent
	# the latest datasets were published.  The more recent the dataset, the darker the cell.
	current_time = datetime.datetime.now()
	def _time_green(_dt):
		if time_shade:
			diff = current_time - _dt
			if diff.days > 28:  # older than a month
				return "BBF7BB"
			elif diff.days > 7: # older than a week
				return "32E732"
			else:				# within a week
				return "15B715"
		else:
			return "A9F5A9"

	print "<table border=\"1\" cellspacing=\"2\" cellpadding=\"4\">"
	print "<tr><th>source_id</th>"

	for col in col_names:
		print header_cell.format(col)

	print "</tr>"

	for source_id in source_id_list:
		print row_cell_b.format(source_id)

		for col in col_names:
			if col in holdings[source_id].keys():	
				num_found = len(holdings[source_id][col])
				latest = max(holdings[source_id][col])
				print cell.format(_time_green(latest), num_found)
			else:
				print cell.format(GRAY,MISSING)

		print "</tr>"

	print "</table>"


def get_data(project):

	search_url = 'https://esgf-node.llnl.gov/esg-search/search' \
				'?project={project}&offset={offset}&limit={limit}' \
				'&fields=_timestamp%2Cexperiment_id%2Csource_id%2Cactivity_id' \
				'&facets=source_id%2Cactivity_id%2Cexperiment_id' \
				'&format=application%2fsolr%2bjson&replica=false'

	# Get source_id and activity_id lists
	req = requests.get(search_url.format(project=project, offset=0, limit=0))
	js = json.loads(req.text)

	activity_id_list = js["facet_counts"]["facet_fields"]["activity_id"][::2]
	source_id_list = js["facet_counts"]["facet_fields"]["source_id"][::2]

	# Get the list of data holdings
	holdings = []
	num_found = js["response"]["numFound"]
	limit = 10000  # This is currently the maximum number of datasets that can be retrieved from esgf-node.llnl.gov/esg-search
	offset = 0
	while offset < num_found:
		r = requests.get(search_url.format(project=project, offset=offset, limit=limit))
		j = json.loads(r.text)
		holdings += j['response']['docs']
		offset += limit

	return (source_id_list, activity_id_list, holdings)


def gen_tables(project, time_shade):

	CMIP_EXP = ["historical", "piControl", "1pctCO2", "amip", "abrupt-4xCO2"]
	BR= "<br><br>"  # Adjust for space

	Experiment_TXT = "Number of 'datasets' [variables x (# of simulations)] from each model for each of the core experiments (DECK + historical)."

	Activity_TXT = "Number of 'datasets' [variables x (# of simulations)]  from each model in support of each CMIP6 activity."

	timestamp = datetime.datetime.now().strftime("%A %d %B %Y %H:%M:%S")
	headstr = "ESGF CMIP6 data holdings as of {}"

	print headstr.format(timestamp)

	# Load all the source ids currently published and get lists 
	source_id_list, activity_id_list, data_holdings = get_data(project)

	# Organize timestamps of published datasets by source, activity, and experiment ID
	activity_holdings = collections.defaultdict(dict)
	experiment_holdings = collections.defaultdict(dict)

	for s in source_id_list:
		activity_holdings[s] = collections.defaultdict(list)
		experiment_holdings[s] = collections.defaultdict(list)

	for d in data_holdings:
		sid = d['source_id'][0]
		aid = d['activity_id'][0]
		eid = d['experiment_id'][0]
		dt = datetime.datetime.strptime(d['_timestamp'][:19], '%Y-%m-%dT%H:%M:%S')
		activity_holdings[sid][aid].append(dt)
		experiment_holdings[sid][eid].append(dt)

	print BR

	# time shading legend
	if time_shade:
		print "The cells are shaded by how recent their latest datasets were published."
		print BR
		print "<table border=\"1\" cellspacing=\"2\" cellpadding=\"4\"><tr>"
		print '<td bgcolor="#BBF7BB">Older than 28 days</td>'
		print '<td bgcolor="#32E732">Older than 7 days</td>'
		print '<td bgcolor="#15B715">Within 7 days</td>'
		print "</tr></table><br>"

	# activity table
	print Activity_TXT
	print BR

	build_table(activity_holdings, source_id_list, activity_id_list, time_shade)

	# experiment table
	print BR
	print Experiment_TXT
	print BR

	build_table(experiment_holdings, source_id_list, CMIP_EXP, time_shade)


def main():

	parser = argparse.ArgumentParser(description="Create HTML tables for the data holdings of ESGF")
	parser.add_argument("--project", "-p", dest="project", type=str, default="CMIP6", help="MIP project name (default is CMIP6)")
	parser.add_argument("--timeshade", help="Shade cells based on how recently the datasets were published", action="store_true")
	args = parser.parse_args()

	gen_tables(args.project, args.timeshade)


if __name__ == '__main__':
	main()
