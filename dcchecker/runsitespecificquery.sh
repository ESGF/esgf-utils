#!/bin/bash

cd /root/scripts/plunger-scripts

prj=$1;
prjfile=$2;
firsttime=$3;


echo -n >ssqueryout.$prj
for i in `cat $prjfile`; do
	echo $i|grep '^#' >/dev/null;
	if [ $? -eq 0 ]; then
		continue;
	fi
	python query.py --proj $prj --datanode $i >>ssqueryout.$prj; 
done
if [ $firsttime -eq 1 ]; then
	cp ssqueryout.$prj oldssqueryout.$prj;
fi
res=`diff oldssqueryout.$prj ssqueryout.$prj -U1`;
if [ "$res" = "" ]; then
	echo "No change";
	cat ssqueryout.$prj;
else
	echo "Changes found:-";
	echo "$res";
fi
