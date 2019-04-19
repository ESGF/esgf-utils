from __future__ import print_function
import requests
import os
import json
import datetime
import argparse
import collections
import jinja2


def get_solr_query_url():
    search_url = 'https://esgf-node.llnl.gov/esg-search/search/' \
                 '?limit=0&format=application%2Fsolr%2Bjson'

    req = requests.get(search_url)
    js = json.loads(req.text)
    shards = js['responseHeader']['params']['shards']

    solr_url = 'https://esgf-node.llnl.gov/solr/datasets/select' \
               '?q=*:*&wt=json&facet=true&fq=type:Dataset' \
               '&fq=replica:false&fq=latest:true&shards={shards}&{{query}}'
    
    return solr_url.format(shards=shards)


def get_latest_data_holdings(project, row_facet, col_facet, selected_columns=None, activity_id=None):
	solr_url = get_solr_query_url()

	if activity_id is None:
		query = 'rows=0&fq=project:{project}' \
				'&facet.field={row_facet}&facet.field={col_facet}' \
				'&stats=true&stats.field={{!tag=piv max=true}}_timestamp' \
				'&facet.pivot={{!stats=piv}}{row_facet},{col_facet}'
		query_url = solr_url.format(query=query.format(project=project, 
													row_facet=row_facet, 
													col_facet=col_facet))
	else:
		query = 'rows=0&fq=project:{project}&fq=activity_id:{activity_id}' \
				'&facet.field={row_facet}&facet.field={col_facet}' \
				'&stats=true&stats.field={{!tag=piv max=true}}_timestamp' \
				'&facet.pivot={{!stats=piv}}{row_facet},{col_facet}'
		query_url = solr_url.format(query=query.format(project=project, 
													activity_id=activity_id,
													row_facet=row_facet, 
													col_facet=col_facet))
	req = requests.get(query_url)
	js = json.loads(req.text)

	rows = js['facet_counts']['facet_fields'][row_facet][::2]
	if selected_columns is None:
		columns = js['facet_counts']['facet_fields'][col_facet][::2]
	else:
		columns = selected_columns
	row_totals = {k: 0 for k in rows}
	column_totals = {k: 0 for k in columns}
	total = 0

	current_time = datetime.datetime.now()
	pivot = js['facet_counts']['facet_pivot'].keys()[0]
	result = {}
	for row in js['facet_counts']['facet_pivot'][pivot]:
		row_val = {}
		for col in row['pivot']:
			if col['value'] in columns:
				ts_str = col['stats']['stats_fields']['_timestamp']['max']
				timestamp = datetime.datetime.strptime(ts_str[:19], '%Y-%m-%dT%H:%M:%S')
				diff = current_time - timestamp
				row_val[col['value']] = dict(num=col['count'], days=diff.days)
				row_totals[row['value']] += 1
				column_totals[col['value']] += 1
		total += row_totals[row['value']]
		result[row['value']] = row_val
		
	holdings = dict(row_totals=row_totals, 
					column_totals=column_totals, 
					total=total, 
					datasets=result)
	return (rows, columns, holdings)


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


def get_facet_value_count(project, row_facet, col_facet, count_facet, selected_columns=None, activity_id=None):
	solr_url = get_solr_query_url()

	if activity_id is None:
		query = 'rows=0&fq=project:{project}' \
		'&facet.field={row_facet}&facet.field={col_facet}' \
		'&stats=true&stats.field={{!tag=piv countDistinct=true}}{count_facet}' \
		'&facet.pivot={{!stats=piv}}{row_facet},{col_facet}'
		query_url = solr_url.format(query=query.format(project=project, 
													row_facet=row_facet, 
													col_facet=col_facet,
													count_facet=count_facet))
	else:
		query = 'rows=0&fq=project:{project}&fq=activity_id:{activity_id}' \
		'&facet.field={row_facet}&facet.field={col_facet}' \
		'&stats=true&stats.field={{!tag=piv countDistinct=true}}{count_facet}' \
		'&facet.pivot={{!stats=piv}}{row_facet},{col_facet}'
		query_url = solr_url.format(query=query.format(project=project,
													activity_id=activity_id,
													row_facet=row_facet, 
													col_facet=col_facet,
													count_facet=count_facet))
	req = requests.get(query_url)
	js = json.loads(req.text)

	rows = js['facet_counts']['facet_fields'][row_facet][::2]
	if selected_columns is None:
		columns = js['facet_counts']['facet_fields'][col_facet][::2]
	else:
		columns = selected_columns

	pivot = js['facet_counts']['facet_pivot'].keys()[0]
	result = {}
	for row in js['facet_counts']['facet_pivot'][pivot]:
		row_val = {}
		for col in row['pivot']:
			if col['value'] in columns:
				num = col['stats']['stats_fields'][count_facet]['countDistinct']
				row_val[col['value']] = num
		result[row['value']] = row_val
			
	return (rows, columns, result)


def gen_tables(project, output_dir):

	CMIP_EXP = ["historical", "piControl", "1pctCO2", "amip", "abrupt-4xCO2"]

	timestamp = datetime.datetime.now().strftime("%A %d %B %Y %H:%M:%S")

	holdings_loader = jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),'esgf_holdings_template.html'))
	holdings_env = jinja2.Environment(loader=holdings_loader)
	holdings_template = holdings_env.get_template('')

	# Create a page with ESGF holdings for all activities of this project
	source_id_list, activity_id_list, activity_holdings = get_latest_data_holdings(project, 'source_id', 'activity_id')
	_source_id_list, _activity_id_list, exp_sim_counts = get_exp_sim_stats(project, 'source_id', 'activity_id')
	_source_id_list, _activity_id_list, variable_counts = get_facet_value_count(project, 'source_id', 'activity_id', 'variable_id')
	frequency_list, _activity_id_list, model_counts = get_facet_value_count(project, 'frequency', 'activity_id', 'source_id')
	html = holdings_template.render(project=project,
									timestamp=timestamp,
									models=source_id_list, 
									activities=activity_id_list, 
									frequencies=frequency_list,
									activity_holdings=activity_holdings,
									exp_sim_counts=exp_sim_counts,
									variable_counts=variable_counts,
									models_per_frequency=model_counts)

	filepath = os.path.join(output_dir, project+'_esgf_holdings.html')
	with open(filepath,'w') as f:
		print(html, file=f)

	# Create pages with ESGF holdings for each activity of this project
	# Display only data for the given list of experiments

	activities_loader = jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),'esgf_activities_template.html'))
	activities_env = jinja2.Environment(loader=activities_loader)
	activities_template = activities_env.get_template('')

	for activity_id in activity_id_list:
		source_id_list, experiment_id_list, experiment_holdings = get_latest_data_holdings(project, 'source_id', 'experiment_id', 
																	activity_id=activity_id)
		_source_id_list, _experiment_id_list, simulation_counts = get_facet_value_count(project, 'source_id', 'experiment_id', 'variant_label',
																	activity_id=activity_id)
		_source_id_list, _experiment_id_list, variable_counts = get_facet_value_count(project, 'source_id', 'experiment_id', 'variable_id', 
																	activity_id=activity_id)
		frequency_list, _experiment_id_list, model_counts = get_facet_value_count(project, 'frequency', 'experiment_id', 'source_id', 
																	activity_id=activity_id)
		html = activities_template.render(project=project,
										activity=activity_id,
										timestamp=timestamp,
										models=source_id_list, 
										experiments=experiment_id_list, 
										frequencies=frequency_list,
										experiment_holdings=experiment_holdings,
										simulation_counts=simulation_counts,
										variable_counts=variable_counts,
										models_per_frequency=model_counts)

		activities_dir = os.path.join(output_dir, activity_id)
		if not os.path.isdir(activities_dir):
			os.mkdir(activities_dir)

		filepath = os.path.join(activities_dir, 'index.html')
		with open(filepath,'w') as f:
			print(html, file=f)


def main():

	parser = argparse.ArgumentParser(description="Create HTML tables for the data holdings of ESGF")
	parser.add_argument("--project", "-p", dest="project", type=str, default="CMIP6", help="MIP project name (default is CMIP6)")
	parser.add_argument("--output", "-o", dest="output", type=str, default=os.path.curdir, help="Output directory (default is current directory)")
	args = parser.parse_args()

	if not os.path.isdir(args.output):
		print("{} is not a directory. Exiting.".format(args.output))
		return
	
	gen_tables(args.project, args.output)


if __name__ == '__main__':
	main()
