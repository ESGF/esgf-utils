#!/bin/bash

release_major_version=1.7
script_version='v1.7.2-phoenix-release-master'
script_release='Phoenix Release'

####Do not change below this line####
replace_version='v0.0.0-devel'
replace_release='Flatbush'
quotedsv=`echo "$replace_version" | sed 's/[./*?|]/\\\\&/g'`;
quotedsr=`echo "$replace_release" | sed 's/[./*?|]/\\\\&/g'`;

echo -n >listoffiles;
declare -A components
components[esgf-dashboard]='bin/esg-dashboard INSTALL README LICENSE'
components[esgf-desktop]='bin/esg-desktop INSTALL README LICENSE'
components[esgf-idp]='bin/esg-idp INSTALL README LICENSE'
components[esgf-installer]='esg-bootstrap esg-node esg-functions esg-gitstrap esg-node.completion esg-purge.sh esg-autoinstall-testnode compute-tools/esg-compute-languages compute-tools/esg-compute-tools INSTALL README LICENSE'
components[esgf-node-manager]='bin/esg-node-manager bin/esgf-sh bin/esgf-spotcheck etc/xsd/registration/registration.xsd INSTALL README LICENSE'
components[esgf-security]='bin/esgf-user-migrate bin/esg-security bin/esgf-policy-check INSTALL README LICENSE'
components[esgf-web-fe]='bin/esg-web-fe INSTALL README LICENSE'
components[esg-orp]='bin/esg-orp INSTALL README LICENSE'
components[esgf-getcert]='INSTALL README LICENSE'
components[esg-search]='bin/esg-search bin/esgf-crawl bin/esgf-optimize-index etc/conf/jetty/jetty.xml-auth etc/conf/jetty/realm.properties etc/conf/solr/schema.xml etc/conf/solr/solrconfig.xml etc/conf/solr/solrconfig.xml-replica etc/conf/solr/solr.xml-master etc/conf/solr/solr.xml-slave etc/conf/jetty/webdefault.xml-auth INSTALL README LICENSE'
rm -rf final-dists
rm -rf temp-dists
mkdir final-dists
mkdir temp-dists
for i in "${!components[@]}"; do
	if [ ! -d $i ]; then
		echo "Directory $i not found. Bailing out.";
		continue;
	fi
	cp $i/dist/* temp-dists;
	rm temp-dists/ivy*.xml;
	for file in ${components[$i]}; do
		if [ ! -e $i/$file ]; then
			echo "File $i/$file not found";
			continue;	
		else  
			echo "File $i/$file OK";
			cp $i/$file temp-dists
		fi
	done
	cd temp-dists;
	for f in `ls`; do 
		if echo $f|grep md5 >/dev/null; then 
			continue; 
		else 
			if [ "$f" = "esg-node" ]; then
				sed -i "s/\(script_version=\"$quotedsv\"\)/script_version=\"$script_version\"/" esg-node;
				sed -i "s/\(script_release=\"$quotedsr\"\)/script_release=\"$script_release\"/" esg-node;
			fi
			md5sum $f >$f.md5; 
		fi
	 done
	if [ "$i" = "esgf-installer" ]; then
		mkdir $release_major_version;
		mv esg-node esg-node.md5 esg-bootstrap esg-bootstrap.md5 $release_major_version/;
	fi
	tar -czf $i-dist.tgz *;
	mv $i-dist.tgz ../final-dists
	cd ..
	rm -rf temp-dists/*
	tar -tf final-dists/$i-dist.tgz |while read ln; do
		val=`echo $ln|sed '/\(.*\/$\)/d'`;
		echo "$i/$ln">>listoffiles;
	done
done
