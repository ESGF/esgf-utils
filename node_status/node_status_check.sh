date > /tmp/todaysdate

source /usr/local/conda/bin/activate

nohup python /usr/local/esgf-utils/node_status/query_prom.py --prom-host aims4.llnl.gov/prometheus -o /esg/config/esgf_datanode_status.json > /var/log/query_prom.log

