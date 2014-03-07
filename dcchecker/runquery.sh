#!/bin/bash

cd /root/scripts/plunger-scripts

firsttime=$1
if [ $# -eq 0 ]; then
	firsttime=0;
fi

dostuff() {
	echo -n >queryout.$prj
	for i in `cat fednodes`; do
		echo $i|grep '^#' >/dev/null;
		if [ $? -eq 0 ]; then
			continue;
		fi
		python query.py --proj $prj $i >>queryout.$prj; 
		done
	if [ $firsttime -eq 1 ]; then
		cp queryout.$prj oldqueryout.$prj;
	fi
	res=`diff oldqueryout.$prj queryout.$prj -U1`;
	if [ "$res" = "" ]; then
		echo "No change";
		cat queryout.$prj;
	else
		echo "Changes found:-";
		echo "$res";
	fi
	echo "Now running site-specific dataset count checks for Project $prj";
	bash runsitespecificquery.sh $prj $prjfile $firsttime
}

while read ln; do
        prj=`echo $ln|cut -d ':' -f1`;
        prjfile=`echo $ln|cut -d ':' -f2`;
		echo "Running dataset count checks for Project $prj";
        dostuff;
done <activatedchecks;
