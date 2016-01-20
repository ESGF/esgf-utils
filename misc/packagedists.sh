#!/bin/bash

script_maj_version=2.2
script_version='v2.2.2-devel-release'
script_release='Centaur'

####Do not change below this line####
replace_version='v2.0-RC5.4.0-devel'
replace_script_maj_version=2.0
replace_release='Centaur'
quotedsv=`echo "$replace_version" | sed 's/[./*?|]/\\\\&/g'`;
quotedsr=`echo "$replace_release" | sed 's/[./*?|]/\\\\&/g'`;
quotedmj=`echo $replace_script_maj_version|sed 's/[./*?|]/\\\\&/g'`;

echo -n >listoffiles;
declare -A components
components[esgf-dashboard]='bin/esg-dashboard INSTALL README LICENSE'
components[esgf-desktop]='bin/esg-desktop INSTALL README LICENSE'
components[esgf-idp]='bin/esg-idp INSTALL README LICENSE'
components[esgf-installer]='jar_security_scan setup-autoinstall globus/esg-globus esg-bootstrap esg-node esg-init esg-functions esg-gitstrap esg-node.completion esg-purge.sh esg-autoinstall-testnode compute-tools/esg-compute-languages compute-tools/esg-compute-tools INSTALL README LICENSE'
components[esgf-node-manager]='bin/esg-node-manager bin/esgf-sh bin/esgf-spotcheck etc/xsd/registration/registration.xsd INSTALL README LICENSE'
components[esgf-security]='bin/esgf-user-migrate bin/esg-security bin/esgf-policy-check INSTALL README LICENSE'
#components[esgf-web-fe]='bin/esg-web-fe INSTALL README LICENSE'
components[esg-orp]='bin/esg-orp INSTALL README LICENSE'
components[esgf-getcert]='INSTALL README LICENSE'
components[esg-search]='bin/esg-search bin/esgf-crawl bin/esgf-optimize-index etc/conf/jetty/jetty.xml-auth etc/conf/jetty/realm.properties etc/conf/solr/schema.xml etc/conf/solr/solrconfig.xml etc/conf/solr/solrconfig.xml-replica etc/conf/solr/solr.xml-master etc/conf/solr/solr.xml-slave etc/conf/jetty/webdefault.xml-auth INSTALL README LICENSE'
components[esgf-product-server]='esg-product-server'
components[filters]='esg-access-logging-filter esg-drs-resolving-filter esg-security-las-ip-filter esg-security-tokenless-filters' 
components[esgf-cog]='esg-cog'
rm -rf final-dists
rm -rf temp-dists
mkdir final-dists
mkdir temp-dists
mkdir esgf-product-server 2>/dev/null
mkdir filters 2>/dev/null
mkdir esgf-cog 2>/dev/null
cp esgf-installer/product-server/* esgf-product-server/
cp esgf-installer/cog/esg-cog esgf-cog
cp esgf-installer/filters/* filters/
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
				sed -i "s/\(script_maj_version=\"$quotedmj\"\)/script_maj_version=\"$script_maj_version\"/" esg-node;
			fi
			if [ "$f" = "esg-bootstrap" ]; then
				sed -i "s/\(script_maj_version=\"$quotedmj\"\)/script_maj_version=\"$script_maj_version\"/" esg-bootstrap;
			fi
			md5sum $f >$f.md5; 
		fi
	 done
	if [ "$i" = "esgf-installer" ]; then
		mkdir $script_maj_version;
		mv esg-node* jar_security_scan* setup-autoinstall* esg-purge.sh* esg-init* esg-functions* esg-bootstrap* $script_maj_version/;
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
