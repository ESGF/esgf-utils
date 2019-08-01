esgf-utils
==========

General ESGF utilities for system testing and monitoring

Contents
=========
1. dcchecker: scripts to monitor dataset counts across the federation, with installer.
2. esgf-openid-resolver: tool to resolve openids issued by federation IDPs.
3. node_status: scripts to query the Prometheus API reporting status of data nodes THREDDS.  Install using: 

```ansible-playbook -i <host-file> --tags index install_ns.yml```

We suggest you become familiar with the Ansible installation, (see Ansible Docs) for additional arguments to run the playbooks.  In addition, please contact LLNL to add the IP of your index node to the access list on the monitoring service API.


