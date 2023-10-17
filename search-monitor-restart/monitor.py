import os
import requests
import json

from time import sleep

URL = "https://esgf-node.llnl.gov/esg-search/search/?limit=0&facets=index_node&format=application%2Fsolr%2Bjson"
ANSIBLE_RESTART = "ansible-playbook -i esgf.hosts --limit esgf-node.llnl.gov stop.yml start.yml"

def do_check():

    resp = requests.get(URL)

    print(type(resp.status_code), resp.status_code)

    if resp.status_code != 200:
        print("Need to Restart")
#        os.system(ANSIBLE_RESTART)
#        return


    try:
        jo = json.loads(resp.text)
        facets = jo["facet_counts"]["facet_fields"]["index_node"]    

        if len(facets) < 4:
            print("Need to restart")
            #os.system(ANSIBLE_RESTART)
            return
    except BaseException as ex:
        print("JSON Parse error or other", ex)

while (True):
    do_check()
    sleep(600)