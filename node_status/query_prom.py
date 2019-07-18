from logging.handlers import RotatingFileHandler
import argparse
import json
import logging
import sys
import time

import requests

def make_req(host):
    # Make a request to the prometheus API
    api_path = "/api/v1/query"
    query_path = f"https://{host}{api_path}"
    r = requests.get(
        query_path, 
        params={
            'query': 'probe_success{job="http_2xx", target=~".*thredds.*"}'
        }
    )
    r.raise_for_status()
    res = r.json()
    return reformat(res['data']['result'])


def reformat(res):
    # Format the output to be very simple, instance : {'status': status, 'time': time}
    out = {}
    for item in res:
        instance = item['metric']['instance']
        status = int(item['value'][1])
        time = int(item['value'][0])
        out[instance] = {'status': status, 'time': time}
    return out

def main():

    # Setup command line
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--prom-host',
        help='Prometheus host that is serving status info. Include any additional paths if not on root path of web server. Ex: "aims4.llnl.gov/prometheus"',
        required=True
    )
    parser.add_argument(
        '-o','--out',
        help='Destination for file that contains info about site statuses',
        required=True
    )
    parser.add_argument(
        '-l','--log',
        help='Log file that will contain messages from requests module',
        default='status.log'
    )
    args = parser.parse_args()

    # Setup logging
    handler = RotatingFileHandler(args.log, maxBytes=100*pow(2,20), backupCount=3)
    logging.basicConfig(
        handlers=[handler],
        level=logging.DEBUG
    )

    # Perform request
    try:
        res = make_req(args.prom_host)
        with open(args.out, 'w') as outfilep:
            json.dump(res, outfilep, indent=2, sort_keys=True)
    except Exception as e:
        logging.error(str(e))
        sys.exit(1)

    logging.info("Success")

main()
