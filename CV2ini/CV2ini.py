import sys
import json

# This script assembles a .ini file for the esg-publisher provided a WCRP .json CV files and additinal static content.
# the CV files are found in https://github.com/WCRP-CMIP/CMIP6_CVs.git
# The static content is found in  https://ithub.com/ESGF/config.git  under publisher-configs/ini/esg.cmip6.ini.static.txt

if len(sys.argv) == 1:
  print "Usage:"
  print  "     python CV2ini.py <project-name> <base-path> <static-content> > <output-file>"
  print
  print "where <base-path> is the location of the CV repo"
  exit(0)




project_in = sys.argv[1]
base_path_in = sys.argv[2]


# TODO : hardcoded values to be replaced by input .json files

facet_dict = { 
               "institute": "institution_id",
               "model": "source_id", 
               "experiment": "", 
               "ensemble": "variant_label", 
               "cmor_table": "table_id", 
               "grid_label": "grid_label" }



DRS_list = [ "mip_era", 
            "activity_id",  
               "institute",
               "model",
               "experiment",
               "ensemble",
               "cmor_table",
               "variable",
               "grid_label",
               "version" ]


delimited_facets = { "realm": "space"}

def load_and_print_static():

  f = open(sys.argv[3])
  for line in f:
    print line.rstrip()

def print_delimited():

    for x in delimited_facets:

        print x + "_delimiter = " + delimited_facets[x]



extract_global_attrs = [  "realm", "frequency", "product",  "nominal_resolution", "source_type", "grid", "branch_method", "source_id", "table_id", "variant_label", "instiution_id"  ]

def print_extract_attrs():

    print "extract_global_attrs = " + ', '.join(extract_global_attrs)

"""
Also handles the cohort map generation
"""
def gen_models_table_entries_and_print(base_path, project):
    

    f=open(base_path + "/" + project + "_source_id.json")

    sidjobj = json.loads(f.read())
    f.close()

    f=open(base_path + "/" + project + "_institution_id.json")
    

    insts = json.loads(f.read())
    f.close()

    outf = open("esgcet_models_table.part.txt", "w")

    print "model_options = " + ', '.join(sidjobj["source_id"].keys())

    print "institute_options = " + ', '.join(insts["institution_id"].keys())

    print "model_cohort_map = map(model : model_cohort)"

    for key in sidjobj["source_id"].keys():

        child = sidjobj["source_id"][key]
        src_str = child["label_extended"]
        inst_keys = child["institution_id"]
        cohorts = " ".join(child["cohort"])
          
        if len(cohorts) < 1:
          cohorts = "none"
            
        print "   " + key + " | " + cohorts
        inst_arr = []

        for n in inst_keys:

            inst_arr.append(insts["institution_id"][n])



        outarr = [project.lower(), key, " ", ', '.join(inst_arr) + ", " + src_str]

        outf.write('  ' +  ' | '.join(outarr) + "\n")
    outf.close()
    print

def get_facet_list(first_item, vers):

    outarr = []
    if len(first_item) > 0:

      outarr = [first_item]
 

    for x in DRS_list:
        
        if (vers or (x != "version")):

            outarr.append("%(" + x + ")s")

    return outarr

def print_directory_format():

    outarr = get_facet_list("/%(root)s", True)


    print "directory_format = " + '/'.join(outarr)



def print_dataset_id_fmt():
    
    outarr = get_facet_list("", False)
    
    print "dataset_id = " + '.'.join(outarr)


def write_options_list(base_path, project, facet_in, facet_out):

    f=open(base_path + "/" + project + "_" + facet_in + ".json")

    jobj = json.loads(f.read())[facet_in]
    
    print facet_out + "_options = " + ', '.join(jobj)


def write_experiment_options(base_path, project):

    f=open(base_path + "/" + project + "_experiment_id.json")
    
    jobj = json.loads(f.read())["experiment_id"]

    print "experiment_options ="
    for key in jobj:

        print "  " +  project.lower() + " | " + key + " | " + jobj[key]["description"].replace('%', "pct")


def write_categories():

#    f = open(ext_file)

    print "categories ="
    print "  project  | enum | true | true | 0"

    omit_list = [ "variable", "version"]

    for i, facet_out in enumerate(facet_dict):

        if not facet_out in omit_list:
        
          type_str = "enum"

          if facet_out == "ensemble":
              type_str = "string"

          outarr = [facet_out, type_str, "true", "true" , str(i + 1)  ]
        
          conv = facet_dict[facet_out]

          print "   " + ' | '.join(outarr)

    base = len(facet_dict) + 1

    for i, facet_out in enumerate(extract_global_attrs + ["model_cohort"]):
    
        outarr = [facet_out, "string", "false", "true" , str(i + base)  ]
        print "   " + ' | '.join(outarr)

    print "  description  | text | false | false | 99"

print "[project:" + project_in.lower() + "]"

load_and_print_static()

write_categories()

gen_models_table_entries_and_print(base_path_in, project_in)
write_experiment_options(base_path_in, project_in)

# TODO get options list
for f_out in ["cmor_table", "grid_label"]:

    
    f_in = facet_dict[f_out]

    if len(f_in) == 0:
        f_in = f_out


    write_options_list(base_path_in, project_in, f_in, f_out)    

write_options_list(base_path_in, project_in, "activity_id", "activity_id")    

print_directory_format()
print_dataset_id_fmt()
print_delimited()
print_extract_attrs()
