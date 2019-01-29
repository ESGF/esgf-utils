import requests
import json
import datetime
import argparse
import collections


def build_holdings_table(holdings, source_id_list, col_total_name, col_names, time_shade=False):

	table_counts = collections.defaultdict(dict)
	source_totals = {k: 0 for k in source_id_list}
	column_totals = {k: 0 for k in col_names}
	total_models = 0

	# counts and totals
	for source_id in source_id_list:
		table_counts[source_id] = collections.defaultdict(dict)

		for col in col_names:
			if col in holdings[source_id].keys():	
				num_found = len(holdings[source_id][col])
				latest = max(holdings[source_id][col])
				table_counts[source_id][col] = {'num': num_found, 'timestamp': latest}
				source_totals[source_id] += 1
				column_totals[col] += 1
		total_models += source_totals[source_id]

	GRAY = "CCCCCC"
	MISSING = ""

	header_cell = "<th>{}</th>"
	row_cell_b="<tr><td><b>{}</b></td>"
	cell = '<td bgcolor="#{}">{}</td>'
	cell_bold = '<td><b>{}</b></td>'

	# If time_shade is enabled, then the cells will be shaded by how recently
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

	print "<div style=\"overflow-x:auto;\">"
	print "<table border=\"1\" cellspacing=\"2\" cellpadding=\"4\">"
	print "<tr><th>source_id</th>"

	for col in [col_total_name] + col_names:
		print header_cell.format(col)

	print "</tr>"

	print row_cell_b.format('# of models')
	print cell_bold.format(total_models)

	for col in col_names:
		print cell_bold.format(column_totals[col])

	print "</tr>"

	for source_id in source_id_list:
		print row_cell_b.format(source_id)
		print cell_bold.format(source_totals[source_id])

		for col in col_names:
			if col in table_counts[source_id].keys():	
				num_found = table_counts[source_id][col]['num']
				latest = table_counts[source_id][col]['timestamp']
				print cell.format(_time_green(latest), num_found)
			else:
				print cell.format(GRAY,MISSING)

		print "</tr>"

	print "</table>"
	print "</div>"


def build_exp_sim_table(exp_sim, source_id_list, col_names):

	exp_sim_counts = collections.defaultdict(dict)

	# Find total number of experiments and simulations
	for source_id in source_id_list:
		exp_sim_counts[source_id] = collections.defaultdict(dict)

		for col in col_names:
			if col in exp_sim[source_id].keys():
				num_exp = 0
				num_sim = 0
				for exp, sims in exp_sim[source_id][col].items():
					num_exp += 1
					num_sim += len(sims)
				exp_sim_counts[source_id][col] = {'num_exp': num_exp, 'num_sim': num_sim}

	WHITE = "FFFFFF"
	GRAY = "CCCCCC"
	MISSING = ""

	header_cell = "<th>{}</th>"
	row_cell_b="<tr><td><b>{}</b></td>"
	cell = '<td bgcolor="#{}">{}</td>'

	print "<div style=\"overflow-x:auto;\">"
	print "<table border=\"1\" cellspacing=\"2\" cellpadding=\"4\">"
	print "<tr><th>source_id</th>"

	for col in col_names:
		print header_cell.format(col)

	print "</tr>"

	for source_id in source_id_list:
		print row_cell_b.format(source_id)

		for col in col_names:
			if col in exp_sim_counts[source_id].keys():
				num_exp = exp_sim_counts[source_id][col]['num_exp']
				num_sim = exp_sim_counts[source_id][col]['num_sim']
				data = '{}/{}'.format(num_exp,num_sim)
				print cell.format(WHITE,data)
			else:
				print cell.format(GRAY,MISSING)

		print "</tr>"

	print "</table>"
	print "</div>"


def get_holdings_data(project):

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


def get_exp_sim_data(project, source_id_list, activity_id_list):

	search_url = 'https://esgf-node.llnl.gov/esg-search/search/' \
				'?{query}&offset=0&limit=0&type=Dataset&replica=false' \
				'&facets=mip_era%2Cactivity_id%2Csource_id%2Cexperiment_id%2Cvariant_label' \
				'&format=application%2Fsolr%2Bjson'

	query1 = 'project={proj}&source_id={sid}&activity_id={aid}'
	query2 = 'project={proj}&source_id={sid}&activity_id={aid}&experiment_id={eid}'

	# Get the simulations per experiment for each source and activity
	exp_sim = {}
	for sid in source_id_list:
		adict = {}
		for aid in activity_id_list:
			# Get list of experiments for the activity
			edict = {}
			r1 = requests.get(search_url.format(query=query1.format(proj=project, sid=sid, aid=aid)))
			j1 = json.loads(r1.text)
			exps = j1['facet_counts']['facet_fields']['experiment_id'][::2]
			for eid in exps:
				# Get list of variant_labels (simulations) for the experiment
				r2 = requests.get(search_url.format(query=query2.format(proj=project, sid=sid, aid=aid, eid=eid)))
				j2 = json.loads(r2.text)
				sim_list = j2['facet_counts']['facet_fields']['variant_label'][::2]
				edict[eid] = sim_list
			if len(edict.keys()) > 0:
				adict[aid] = edict
		if len(adict.keys()) > 0:
			exp_sim[sid] = adict

	return exp_sim


def gen_tables(project, time_shade):

	CMIP_EXP = ["historical", "piControl", "1pctCO2", "amip", "abrupt-4xCO2"]
	BR= "<br><br>"  # Adjust for space

	Experiment_TXT = "Number of 'datasets' [variables x (# of simulations)] from each model for each of the core experiments (DECK + historical)."

	Activity_TXT = "Number of 'datasets' [variables x (# of simulations)]  from each model in support of each CMIP6 activity."

	EXP_SIM_TXT = "Number of experiments and simulations [(# of experiments) / (# of simulations)] from each model in support of each CMIP6 activity."

	timestamp = datetime.datetime.now().strftime("%A %d %B %Y %H:%M:%S")
	headstr = "ESGF CMIP6 data holdings as of {}"

	print headstr.format(timestamp)

	# Load all the source ids currently published and get lists 
	source_id_list, activity_id_list, data_holdings = get_holdings_data(project)

	# Organize timestamps of published datasets by source, activity, and experiment ID
	activity_holdings = collections.defaultdict(dict)
	experiment_holdings = collections.defaultdict(dict)

	for s in source_id_list:
		activity_holdings[s] = collections.defaultdict(list)
		experiment_holdings[s] = collections.defaultdict(list)

	for d in data_holdings:
		dt = datetime.datetime.strptime(d['_timestamp'][:19], '%Y-%m-%dT%H:%M:%S')
		for sid in d['source_id']:
			for aid in d['activity_id']:
				activity_holdings[sid][aid].append(dt)
			for eid in d['experiment_id']:
				experiment_holdings[sid][eid].append(dt)

	# Load data for # of experiments / # of simulations
	exp_sim = get_exp_sim_data(project, source_id_list, activity_id_list)

	print BR

	# time shading legend
	if time_shade:
		print "The cells are shaded by how recently their latest datasets were published."
		print BR
		print "<table border=\"1\" cellspacing=\"2\" cellpadding=\"4\"><tr>"
		print '<td bgcolor="#BBF7BB">More than 28 days</td>'
		print '<td bgcolor="#32E732">More than 7 days</td>'
		print '<td bgcolor="#15B715">Less than 7 days</td>'
		print "</tr></table><br>"

	# activity table
	print Activity_TXT
	print BR

	build_holdings_table(activity_holdings, source_id_list, '# of activities', activity_id_list, time_shade)

	# experiment table
	print BR
	print Experiment_TXT
	print BR

	build_holdings_table(experiment_holdings, source_id_list, '# of expts', CMIP_EXP, time_shade)

	# # of experiments / # of simulations table
	print BR
	print EXP_SIM_TXT
	print BR
	
	build_exp_sim_table(exp_sim, source_id_list, activity_id_list)


def main():

	parser = argparse.ArgumentParser(description="Create HTML tables for the data holdings of ESGF")
	parser.add_argument("--project", "-p", dest="project", type=str, default="CMIP6", help="MIP project name (default is CMIP6)")
	parser.add_argument("--timeshade", help="Shade cells based on how recently the datasets were published", action="store_true")
	args = parser.parse_args()

	gen_tables(args.project, args.timeshade)


if __name__ == '__main__':
	main()
