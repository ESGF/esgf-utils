#!/usr/bin/env python

from pyesgf.security import ats
from openid.yadis import discover
from lxml import etree
import socket,sys,argparse

socket.setdefaulttimeout(30)
QUERY_ISSUER='/test/test'
cargs=dict()
cargs['CAINFO']='esgf-ca-bundle.crt'
aparser=argparse.ArgumentParser()
aparser.add_argument('openid',type=str,nargs='?',default='none')
aparser.add_argument('--file',type=str,nargs='?',default='none')
args=aparser.parse_args()
openid=args.openid
fname=args.file
if openid == 'none' and fname == 'none':
	sys.exit(-1)

def doLookup(openid,cargs):
	fail='notfound'
	try:
		discoverresult=discover.discover(openid,cargs)
	except:
		print "ConnectionError: failed to lookup %s"%(openid)
		raise
		return
	
	root=etree.XML(discoverresult.response_text)
	gotcha=0
	s_url=None
	for element in root.iter("*"):
		if gotcha == 1:
			s_url=element.text
			break
		if element.text == 'urn:esg:security:attribute-service':
			gotcha=1
			continue
	if s_url == None:
		print fail
		raise
		sys.exit(-1)
	try:
		s=ats.AttributeService(s_url,QUERY_ISSUER)
	except:
		print fail
		raise
		sys.exit(-1)

	try:
		r=s.send_request(openid,['urn:esg:first:name','urn:esg:last:name','urn:esg:email:address'])
	except:
		print fail
		raise
		sys.exit(-1)
	res=r.get_attributes()
	fn=res['urn:esg:first:name']
	ln=res['urn:esg:last:name']
	emailid=res['urn:esg:email:address']
	print "%s: %s %s (%s)"%(openid,fn,ln,emailid)

if openid != 'none':
	doLookup(openid,cargs)
	sys.exit(0)

try:
	fp=open(fname,'r')
	flines=fp.readlines()
	fp.close()
except:
	print "File access error"
	sys.exit(-1)

for line in flines:
	openid=line.split('\n')[0]
	doLookup(openid,cargs)
