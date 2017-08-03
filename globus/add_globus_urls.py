#!/usr/bin/env python

import os
import sys
import logging
from esgcet.config import loadConfig, getConfig, getThreddsServiceSpecs
from esgcet.publish import thredds
from lxml.etree import SubElement as SE, XMLParser, parse, tostring, fromstring
import urlparse, httplib, urllib


NS = {
    "ns": "http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0",
    "xlink": "http://www.w3.org/1999/xlink",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance"
}
XLINK = "http://www.w3.org/1999/xlink"

global update_all
update_all = False



def add_globus(catalog_path, globus_base):
    if ' ' in catalog_path:
        return

    global update_all

    sys.stdout.write('Processing %s' % catalog_path)


    parser = XMLParser(remove_blank_text=True)

    doc = None
    try:
        doc = parse(catalog_path, parser)
    except:
        print "Parse error on file", catalog_path
        return

    root = doc.getroot()

    fileservice = root.xpath('/ns:catalog/ns:service[@name="fileservice"]', namespaces=NS)[0]
    globus_service = fileservice.findall('ns:service[@serviceType="Globus"]', namespaces=NS)
    if globus_service:
        base = globus_service[0].get('base')
        update = False
        if base != globus_base:
            if update_all:
                update = True
            else:
                print 'A base attribute of the Globus service in %s is\n'\
                      '%s which does not match\n'\
                      '%s set in %s.' % (catalog_path, base, globus_base, os.environ['ESGINI'])
                while True:
                    sys.stdout.write("Do you want to correct it now? [Y/n/all]")
                    line = sys.stdin.readline().rstrip()
                    if line == 'n' or line == 'N':
                        break
                    if line == 'all':
                        update_all = True
                        update = True
                        break
                    if line == '' or line == 'y' or line == 'Y':
                        update = True
                        break
        if update:
            globus_service[0].set('base', globus_base)
            doc.write(catalog_up, xml_declaration=True, encoding='UTF-8', pretty_print=True)
            print " - Done"
        else:
            print " - Nothing to do"
    else:
        service = SE(fileservice, 'service', base=globus_base, desc="Globus Transfer Service", name="Globus", serviceType="Globus")
        SE(service, 'property', name='requires_authorization', value='false')
        SE(service, 'property', name='application', value='Web Browser')
        datasets = root.xpath('/ns:catalog/ns:dataset/ns:dataset', namespaces=NS)
        for dataset in datasets:
            lst = dataset.findall('ns:access[@serviceName="GRIDFTP"]', namespaces=NS)
            if len(lst) > 0:
                gridftp_access = lst[0]
                url_path = gridftp_access.get('urlPath')
                if url_path.startswith('/'):
                    url_path = url_path[1:]
                SE(dataset, 'access', serviceName='Globus', urlPath=url_path)
        doc.write(catalog_path, xml_declaration=True, encoding='UTF-8', pretty_print=True)
        print " - Done"


def process(thredds_root, thredds_root_up, globus_base, thredds_url, esgf_harvesting_service_url, hessian_service_certfile):

    # Process /esg/content/thredds/catalog.xml
    catalog_up = os.path.join(thredds_root_up, 'catalog.xml')
    parser = XMLParser(remove_blank_text=True)
    doc = parse(catalog_up, parser)
    root = doc.getroot()
    fileservice = root.xpath('/ns:catalog/ns:service[@name="fileservice"]', namespaces=NS)[0]
    globus_service = fileservice.findall('ns:service[@serviceType="Globus"]', namespaces=NS)
    if globus_service:
        base = globus_service[0].get('base')
        if base != globus_base:
            print 'The "base" attribute of the Globus service in %s is\n'\
                  '%s which does not match\n'\
                  '%s set in %s.' % (catalog_up, base, globus_base, os.environ['ESGINI'])
            while True:
                sys.stdout.write("Do you want to correct it now? [Y/n]")
                line = sys.stdin.readline().rstrip()
                if line == 'n' or line == 'N':
                    break
                if line == '' or line == 'y' or line == 'Y':
                    globus_service[0].set('base', globus_base)
                    doc.write(catalog_up, xml_declaration=True, encoding='UTF-8', pretty_print=True)
                    break
    else:
        service = SE(fileservice, 'service', base=globus_base, desc="Globus Transfer Service", name="Globus", serviceType="Globus")
        SE(service, 'property', name='requires_authorization', value='false')
        SE(service, 'property', name='application', value='Web Browser')
        doc.write(catalog_up, xml_declaration=True, encoding='UTF-8', pretty_print=True)


    # Get all xml files listed in /esg/content/thredds/esgcet/catalog.xml
    catalog = os.path.join(thredds_root, 'catalog.xml')
    parser = XMLParser(remove_blank_text=True)
    doc = parse(catalog, parser)
    root = doc.getroot()
    catalog_ref = root.xpath('/ns:catalog/ns:catalogRef', namespaces=NS)
    catalog_files = []
    for cr in catalog_ref:
        href = cr.get('{%s}href' % XLINK)
        catalog_files.append(href)
    print 'Found %d THREDDS catalog files to process' % len(catalog_files)

    # Add Globus URLs to all xml files
    for catalog_file in catalog_files:
        catalog_path = os.path.join(thredds_root, catalog_file)
        add_globus(catalog_path, globus_base)

    # re-initialize the THREDDS server
    print "\nReinitializing THREDDS server"
    thredds.reinitializeThredds()

    # re-harvest all catalogs
    print "\nRe-harvesting all catalogs"
    hessian_service_url = urlparse.urlparse(esgf_harvesting_service_url)



#        harvest(catalog_url, hessian_service_url.hostname, hessian_service_url.path, hessian_service_certfile)


def harvest(catalog_url, hessian_service_hostname, hessian_service_path, hessian_service_certfile):

    sys.stdout.write('Harvesting %s' % catalog_url)

    params = urllib.urlencode({'uri': catalog_url, 'metadataRepositoryType': 'THREDDS'})
    conn = httplib.HTTPSConnection(hessian_service_hostname, cert_file=hessian_service_certfile, key_file=hessian_service_certfile) 
    conn.request("POST", hessian_service_path, params)
    resp = conn.getresponse()
    if resp.status == 200:
        print ' - Success'
    elif resp.status == 401:
        root = fromstring(resp.read())
        message = root.xpath('/response/message')[0]
        print '\n        Error - %s' % message.text
    else:
        print '\n        Error %d, %s' % (resp.status, resp.reason)


def main():

    """Uses the esg.ini file options:
        - thredds_file_services
              to get a Globus endpoint UUID
        - thredds_root
              to find a directory with THREDDS xml catalogs
    """

    loadConfig(None)
    config = getConfig()
    if config is None:
        raise ESGPublishError('No configuration file found')

    # By default thredds_root is: /esg/content/thredds/esgcet
    thredds_root = config.get('DEFAULT', 'thredds_root')
    thredds_file_services = getThreddsServiceSpecs(config, 'DEFAULT', 'thredds_file_services')
    # parameters needed to re-harvest the THREDDS catalogs
    thredds_url = config.get('DEFAULT', 'thredds_url')
    hessian_service_certfile = config.get('DEFAULT', 'hessian_service_certfile')
    hessian_service_url = config.get('DEFAULT', 'hessian_service_url')
    esgf_harvesting_service_url = hessian_service_url.replace('remote/secure/client-cert/hessian/publishingService','ws/harvest')

    thredds_root_up = os.path.normpath(os.path.join(thredds_root, '..'))
    globus_base = None
    for service in thredds_file_services:
        if service[2] == 'Globus':
            globus_base = service[1]
    if globus_base is None:
        print 'No Globus file service specified in %s\n'\
              'Add Globus file service to the thredds_file_services variable in the form:\n'\
              '        Globus | globus:<UUID_of_Globus_endpoint_pointing_to_your_data_node_GridFTP_server> | Globus | fileservice\n'\
              'A UUID assigned to the endpoint can be found on https://globus.org/' % os.environ['ESGINI']
        sys.exit(1)

    print '\n'\
          'ESGINI: %s\n'\
          'THREDDS root: %s\n'\
          'THREDDS url: %s\n'\
          'Globus service base: %s\n'\
          'ESGF harvesting service url: %s\n'\
          'X.509 user credential: %s\n'\
          '' % (os.environ['ESGINI'], thredds_root, thredds_url, globus_base, esgf_harvesting_service_url, hessian_service_certfile)

    if not globus_base.endswith('/'):
        print 'Globus service base must end with "/". Set Globus service base correctly in\n'\
              '%s end run the script again.' % os.environ['ESGINI']
        sys.exit(1)

    print 'The script recursively goes through xml files in %s\n'\
          'looking for datasets that were published without Globus file service and adds\n'\
          'Globus access to the datasets. If a dataset was published with Globus file\n'\
          'service configured, the script skips such a dataset leaving a corresponding xml\n'\
          'file unmodified. The script reinitializes THREDDS and requests Hessian service to\n'\
          'to harvest the updated xml files. Because Hessian service requires SSL\n'\
          'authentication, the X.509 certificate, %s,\n'\
          'should be valid and obtained by a user who has the publisher role in all\n'\
          'projects.\n'\
          'It is strongly advised that you make a copy of the entire %s\n'\
          'directory prior to running this script.' % (thredds_root_up, hessian_service_certfile, thredds_root_up)

    while True:
        sys.stdout.write("Do you want to continue? [y/N]")
        line = sys.stdin.readline().rstrip()
        if line == '' or line == 'n' or line == 'N':
            sys.exit(0)
        if line == 'y' or line == 'Y':
            break

    process(thredds_root, thredds_root_up, globus_base, thredds_url, esgf_harvesting_service_url, hessian_service_certfile)


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    main()
