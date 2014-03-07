#!/usr/bin/python
from pyesgf.search import SearchConnection
import os,sys,argparse

aparser=argparse.ArgumentParser()
aparser.add_argument('--proj', type=str,required=True)
aparser.add_argument('--datanode', type=str,default='notdefined')
aparser.add_argument('site', type=str,default='esg-dn1.nsc.liu.se',nargs='?')
args=aparser.parse_args()
site=args.site
proj=args.proj
dnode=args.datanode
if dnode == 'notdefined':
	print 'Commencing checks for datasets belonging to project %s indexed on site %s'%(proj,site)
else:
	print 'Commencing checks for datasets belonging to project %s published on site %s'%(proj,dnode)
searchurl='http://%s/esg-search'%site
exceptexit=0
try:
	conn=SearchConnection(searchurl,distrib=True)
	if dnode != 'notdefined':
		ctx=conn.new_context(project=proj,data_node=dnode,replica=False)
	else:
		ctx=conn.new_context(project=proj,replica=False)
	matches=ctx.search()
	print 'Found %d matches'%len(matches)

except:
	print "Node Failed to Respond"
	exceptexit=1
if exceptexit == 1:
	sys.exit(-1)
