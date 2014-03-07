#!/bin/bash

python test.py;
if [ $? -ne 0 ]; then
	echo -e "esgf-pyclient not found. Please fetch and install from https://github.com/stephenpascoe/esgf-pyclient.git \nCannot proceed till esgf-pyclient is installed. Aborting.";
	exit -1;
fi

echo "Please specify installation directory";
read instdir;
res=`echo $instdir|sed s/[a-zA-Z0-9\ /._-]//g`;
if [ "$res" != "" ]; then
	echo "Invalid directory name. No special characters allowed.";
	exit -1;
fi
echo "Please specify email address for run output";
read cronemail;
res=`echo $cronemail|sed s/[a-zA-Z0-9._@]//g`;
if [ "$res" != "" ]; then
	echo "Invalid email address";
	exit -1;
fi

cronmin=`echo "$RANDOM%60"|bc`;
quoted_inst=`echo "$instdir" | sed 's/[ ]/\\\\&/g'`;
fullyquoted_inst=`echo "$quoted_inst" | sed 's/[/ \.]/\\\&/g'`;

if [ ! -d "$instdir" ]; then
	echo "Directory $instdir does not exist. Create? (y/N)";
	read choice;
	if [ "$choice" != "y" ] && [ "$choice" != "Y" ]; then
		exit -1;
	fi
	echo "Will create directory $instdir";
	mkdir -p "$instdir";
	
	else
		echo "Directory $instdir found. Will use";
fi

echo -n >activatedchecks;
for ln in `cat availablechecks`; do
	prj=`echo $ln|cut -d':' -f1`;
	prjnodesfile=`echo $ln|cut -d':' -f2`;
	echo "Do you wish to run checks for Project $prj? (y/N)";
	read choice;
	if [ "$choice" != "y" ] && [ "$choice" != "Y" ]; then
		continue;
	fi
	echo $ln >>activatedchecks;
done

cat runquery.sh |sed "s/cd \/.*/cd $fullyquoted_inst/" >runquery.sh-tocopy;
cat runsitespecificquery.sh |sed "s/cd \/.*/cd $fullyquoted_inst/" >runsitespecificquery.sh-tocopy;
#write out the cron
echo "# Run dataset count checks" >checkdscount;
echo "MAILTO=$cronemail" >>checkdscount;
echo "$cronmin */6 * * * root bash $quoted_inst/runquery.sh 0" >>checkdscount;

#Copy section

cp cordexnodes cmip5nodes fednodes query.py activatedchecks LICENSE "$instdir/";
cp runquery.sh-tocopy "$instdir/runquery.sh";
cp runsitespecificquery.sh-tocopy "$instdir/runsitespecificquery.sh";

echo "Install done. Will run the first init run and post-install now";
#First run
bash $quoted_inst/runquery.sh 1;

echo "Finishing post-installation";
#Install cron
cp checkdscount /etc/cron.d/
echo "Installation complete :)";
