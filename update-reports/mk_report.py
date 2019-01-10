import requests, sys, json, datetime



PROJECT=sys.argv[1]

#summtable=(len(sys.argv > 2) and sys.argv[2] == "--summtable")
#backfill=(len(sys.argv > 2) and sys.argv[2] == "--backfill")

#PROJECT="CMIP6"

CMIP_EXP = ["historical", "piControl", "1pctCO2", "amip", "abrupt-4xCO2"]

search_url='https://esgf-node.llnl.gov/esg-search/search?project={}&{}&limit={}&format=application%2fsolr%2bjson&replica=false'

GRAY = "CCCCCC"
GREEN = "A9F5A9"
MISSING = ""
BR= "<br><br>"  # Adjust for space


row_cell_b="<tr><td><b>{}</b></td>"
cell = '<td bgcolor="#{}">{}</td>'

Experiment_TXT = "Number of 'datasets' [variables x (# of simulations)] from each model for each of the core experiments (DECK + historical)."

Activity_TXT = "Number of 'datasets' [variables x (# of simulations)]  from each model in support of each CMIP6 activity."

def print_header(TableType, columns, other):

	header_cell = "<th>{}</th>"

	print "<table border=\"1\" cellspacing=\"2\" cellpadding=\"4\">"
	print "<tr><th>source_id</th>"

	for col in columns:

		print header_cell.format(col)

	# if other:
	# 	print "<th>Other</th>"		
	print "</tr>"


def build_matrix(QSTR):


	timestamp = datetime.datetime.now().strftime("%A %d %B %Y %H:%M:%S")
	headstr = "ESGF CMIP6 data holdings as of {}"

	print headstr.format(timestamp)

	# 1 Load all the source ids currently published and get lists 

	resp = requests.get(search_url.format(PROJECT,QSTR,0))

	jobj = json.loads(resp.text)

	scid_dict = {}

	activity_list = jobj["facet_counts"]["facet_fields"]["activity_id"][::2]
	source_id_lst = jobj["facet_counts"]["facet_fields"]["source_id"][::2]


	# query each to get the valid experiments and actvities

	for fname in source_id_lst:
		Qbase = "source_id={}&fields=id&facets=activity_id%2Cexperiment_id"
		QSTR=Qbase.format(fname)

		resp = requests.get(search_url.format(PROJECT,QSTR,0))

		j2 = json.loads(resp.text)

		scid_dict[fname] = j2


	# activity table

	print BR
	print Activity_TXT
	print BR

	print_header("MIP Activities", activity_list, False)


	for fname in source_id_lst:

		d = scid_dict[fname]

		# print the label for
		print row_cell_b.format(fname)

		act_lst = d["facet_counts"]["facet_fields"]["activity_id"]

		act_dict = {}
		for k, v in zip(act_lst[::2], act_lst[1::2]):
			act_dict[k] = v

		for col in activity_list:
			if col in act_dict:	

				print cell.format(GREEN, act_dict[col])
			else:
				print cell.format(GRAY,MISSING)

		print "</tr>"
	print "</table>"

	# experiment table

	print BR
	print Experiment_TXT
	print BR

	print_header("CMIP Experiments", CMIP_EXP, True)

	for fname in source_id_lst:

		d = scid_dict[fname]

		exp_lst = d["facet_counts"]["facet_fields"]["experiment_id"]

		exp_dict = {}
		for k, v in zip(exp_lst[::2], exp_lst[1::2]):
			exp_dict[k] = v

		# print the label for
		print row_cell_b.format(fname)

		for col in CMIP_EXP:
			if col in exp_dict:	

				print cell.format(GREEN, exp_dict[col])
			else:
				print cell.format(GRAY,MISSING)

		print "</tr>"
	print "</table>"



def main():

	QSTR = "facets=source_id%2Cactivity_id&fields=id"

	build_matrix(QSTR)



if __name__ == '__main__':
	main()


#def build_daily_table():


#def backfill_tables(datefrom, dateto):

#	for n in range(datefrom, dateto+1):



#def assemble_page():





