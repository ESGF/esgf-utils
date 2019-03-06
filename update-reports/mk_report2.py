import requests
import json
import datetime
import argparse
import collections


def get_solr_query_url():
    search_url = 'https://esgf-node.llnl.gov/esg-search/search/' \
                 '?limit=0&format=application%2Fsolr%2Bjson'

    req = requests.get(search_url)
    js = json.loads(req.text)
    shards = js['responseHeader']['params']['shards']

    solr_url = 'https://esgf-node.llnl.gov/solr/datasets/select' \
               '?q=*:*&wt=json&facet=true&fq=type:Dataset' \
               '&fq=replica:false&shards={shards}&{{query}}'
    
    return solr_url.format(shards=shards)


def get_latest_data_holdings(project, row_facet, col_facet):
    solr_url = get_solr_query_url()
    
    query = 'rows=0&fq=project:{project}' \
            '&facet.field={row_facet}&facet.field={col_facet}' \
            '&stats=true&stats.field={{!tag=piv max=true}}_timestamp' \
            '&facet.pivot={{!stats=piv}}{row_facet},{col_facet}'
    query_url = solr_url.format(query=query.format(project=project, 
                                                   row_facet=row_facet, 
                                                   col_facet=col_facet))
    req = requests.get(query_url)
    js = json.loads(req.text)
    
    rows = js['facet_counts']['facet_fields'][row_facet][::2]
    columns = js['facet_counts']['facet_fields'][col_facet][::2]
    
    pivot = js['facet_counts']['facet_pivot'].keys()[0]
    result = {}
    for row in js['facet_counts']['facet_pivot'][pivot]:
        row_val = {}
        for col in row['pivot']:
            ts_str = col['stats']['stats_fields']['_timestamp']['max']
            timestamp = datetime.datetime.strptime(ts_str[:19], '%Y-%m-%dT%H:%M:%S')
            row_val[col['value']] = dict(num=col['count'], timestamp=timestamp)
        result[row['value']] = row_val
            
    return (rows, columns, result)


def get_exp_sim_stats(project, row_facet, col_facet):
    solr_url = get_solr_query_url()
    
    query = 'rows=0&fq=project:{project}' \
            '&facet.field={row_facet}&facet.field={col_facet}' \
            '&stats=true&stats.field={{!tag=piv countDistinct=true}}variant_label' \
            '&facet.pivot={{!stats=piv}}{row_facet},{col_facet},experiment_id'
    query_url = solr_url.format(query=query.format(project=project, 
                                                   row_facet=row_facet, 
                                                   col_facet=col_facet))
    req = requests.get(query_url)
    js = json.loads(req.text)
    
    rows = js['facet_counts']['facet_fields'][row_facet][::2]
    columns = js['facet_counts']['facet_fields'][col_facet][::2]
    
    pivot = js['facet_counts']['facet_pivot'].keys()[0]
    result = {}
    for row in js['facet_counts']['facet_pivot'][pivot]:
        row_val = {}
        for col in row['pivot']:
            num_exp = 0
            num_sim = 0
            for exp in col['pivot']:
                num_exp += 1
                num_sim += exp['stats']['stats_fields']['variant_label']['countDistinct']
            row_val[col['value']] = dict(num_exp=num_exp, num_sim=num_sim)
        result[row['value']] = row_val
            
    return (rows, columns, result)


def get_facet_value_count(project, row_facet, col_facet, count_facet):                                           
    solr_url = get_solr_query_url()
    
    query = 'rows=0&fq=project:{project}' \
            '&facet.field={row_facet}&facet.field={col_facet}' \
            '&stats=true&stats.field={{!tag=piv countDistinct=true}}{count_facet}' \
            '&facet.pivot={{!stats=piv}}{row_facet},{col_facet}'
    query_url = solr_url.format(query=query.format(project=project, 
                                                   row_facet=row_facet, 
                                                   col_facet=col_facet,
												   count_facet=count_facet))
    req = requests.get(query_url)
    js = json.loads(req.text)
    
    rows = js['facet_counts']['facet_fields'][row_facet][::2]
    columns = js['facet_counts']['facet_fields'][col_facet][::2]
    
    pivot = js['facet_counts']['facet_pivot'].keys()[0]
    result = {}
    for row in js['facet_counts']['facet_pivot'][pivot]:
        row_val = {}
        for col in row['pivot']:
            num = col['stats']['stats_fields'][count_facet]['countDistinct']
            row_val[col['value']] = num
        result[row['value']] = row_val
            
    return (rows, columns, result)


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
			if col in holdings[source_id].keys():	
				num_found = holdings[source_id][col]['num']
				latest = holdings[source_id][col]['timestamp']
				print cell.format(_time_green(latest), num_found)
			else:
				print cell.format(GRAY,MISSING)

		print "</tr>"

	print "</table>"
	print "</div>"


def build_exp_sim_table(exp_sim_counts, source_id_list, activity_id_list):

	WHITE = "FFFFFF"
	GRAY = "CCCCCC"
	MISSING = ""

	header_cell = "<th>{}</th>"
	row_cell_b="<tr><td><b>{}</b></td>"
	cell = '<td bgcolor="#{}">{}</td>'

	print "<div style=\"overflow-x:auto;\">"
	print "<table border=\"1\" cellspacing=\"2\" cellpadding=\"4\">"
	print "<tr><th>source_id</th>"

	for activity_id in activity_id_list:
		print header_cell.format(activity_id)

	print "</tr>"

	for source_id in source_id_list:
		print row_cell_b.format(source_id)

		for activity_id in activity_id_list:
			if activity_id in exp_sim_counts[source_id].keys():
				num_exp = exp_sim_counts[source_id][activity_id]['num_exp']
				num_sim = exp_sim_counts[source_id][activity_id]['num_sim']
				data = '{}/{}'.format(num_exp,num_sim)
				print cell.format(WHITE,data)
			else:
				print cell.format(GRAY,MISSING)

		print "</tr>"

	print "</table>"
	print "</div>"


def build_var_table(var_counts, source_id_list, activity_id_list):

	WHITE = "FFFFFF"
	GRAY = "CCCCCC"
	MISSING = ""

	header_cell = "<th>{}</th>"
	row_cell_b="<tr><td><b>{}</b></td>"
	cell = '<td bgcolor="#{}">{}</td>'

	print "<div style=\"overflow-x:auto;\">"
	print "<table border=\"1\" cellspacing=\"2\" cellpadding=\"4\">"
	print "<tr><th>source_id</th>"

	for activity_id in activity_id_list:
		print header_cell.format(activity_id)

	print "</tr>"

	for source_id in source_id_list:
		print row_cell_b.format(source_id)

		for activity_id in activity_id_list:
			if activity_id in var_counts[source_id].keys():
				num_vars = var_counts[source_id][activity_id]
				data = '{}'.format(num_vars)
				print cell.format(WHITE,data)
			else:
				print cell.format(GRAY,MISSING)

		print "</tr>"

	print "</table>"
	print "</div>"


def build_model_table(model_counts, frequency_list, activity_id_list):

	WHITE = "FFFFFF"
	GRAY = "CCCCCC"
	MISSING = ""

	header_cell = "<th>{}</th>"
	row_cell_b="<tr><td><b>{}</b></td>"
	cell = '<td bgcolor="#{}">{}</td>'

	print "<div style=\"overflow-x:auto;\">"
	print "<table border=\"1\" cellspacing=\"2\" cellpadding=\"4\">"
	print "<tr><th>frequency</th>"

	for activity_id in activity_id_list:
		print header_cell.format(activity_id)

	print "</tr>"

	for frequency in frequency_list:
		print row_cell_b.format(frequency)

		for activity_id in activity_id_list:
			if activity_id in model_counts[frequency].keys():
				num_models = model_counts[frequency][activity_id]
				data = '{}'.format(num_models)
				print cell.format(WHITE,data)
			else:
				print cell.format(GRAY,MISSING)

		print "</tr>"

	print "</table>"
	print "</div>"


def gen_tables(project, time_shade):

	CMIP_EXP = ["historical", "piControl", "1pctCO2", "amip", "abrupt-4xCO2"]
	BR= "<br><br>"  # Adjust for space

	Experiment_TXT = "Number of 'datasets' [variables x (# of simulations)] from each model for each of the core experiments (DECK + historical)."

	Activity_TXT = "Number of 'datasets' [variables x (# of simulations)]  from each model in support of each CMIP6 activity."

	EXP_SIM_TXT = "Number of experiments and simulations [(# of experiments) / (# of simulations)] from each model in support of each CMIP6 activity."

	Variables_TXT = "Number of variables from each model in support of each CMIP6 activity."

	Models_per_freq_TXT = "Number of models providing output at each sampling frequency in support of each CMIP6 activity."

	timestamp = datetime.datetime.now().strftime("%A %d %B %Y %H:%M:%S")
	headstr = "ESGF CMIP6 data holdings as of {}"

	print headstr.format(timestamp)

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

	source_id_list, activity_id_list, activity_holdings = get_latest_data_holdings(project, 'source_id', 'activity_id')
	build_holdings_table(activity_holdings, source_id_list, '# of activities', activity_id_list, time_shade)

	# experiment table
	print BR
	print Experiment_TXT
	print BR

	source_id_list, experiment_id_list, experiment_holdings = get_latest_data_holdings(project, 'source_id', 'experiment_id')
	build_holdings_table(experiment_holdings, source_id_list, '# of expts', CMIP_EXP, time_shade)

	# # experiments / # of simulations table
	print BR
	print EXP_SIM_TXT
	print BR
	
	source_id_list, _activity_id_list, exp_sim_counts = get_exp_sim_stats(project, 'source_id', 'activity_id')
	build_exp_sim_table(exp_sim_counts, source_id_list, activity_id_list)

	# # variables
	print BR
	print Variables_TXT
	print BR

	source_id_list, _activity_id_list, var_counts = get_facet_value_count(project, 'source_id', 'activity_id', 'variable_id')
	build_var_table(var_counts, source_id_list, activity_id_list)

	# # models 
	print BR
	print Models_per_freq_TXT
	print BR

	frequency_list, _activity_id_list, model_counts = get_facet_value_count(project, 'frequency', 'activity_id', 'source_id')
	build_model_table(model_counts, frequency_list, activity_id_list)


def main():

	parser = argparse.ArgumentParser(description="Create HTML tables for the data holdings of ESGF")
	parser.add_argument("--project", "-p", dest="project", type=str, default="CMIP6", help="MIP project name (default is CMIP6)")
	parser.add_argument("--timeshade", help="Shade cells based on how recently the datasets were published", action="store_true")
	args = parser.parse_args()

	gen_tables(args.project, args.timeshade)


if __name__ == '__main__':
	main()
