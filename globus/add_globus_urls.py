#!/usr/bin/python

import os
import sys
import logging
from esgcet.config import loadConfig, getConfig, getThreddsServiceSpecs
from esgcet.publish import thredds
from lxml.etree import SubElement as SE, XMLParser, parse, tostring


NS = {
    "ns": "http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0",
    "xlink": "http://www.w3.org/1999/xlink",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance"
}
XLINK = "http://www.w3.org/1999/xlink"

def add_globus(catalog_path, globus_base):
    parser = XMLParser(remove_blank_text=True)
    doc = parse(catalog_path, parser)
    root = doc.getroot()

    fileservice = root.xpath('/ns:catalog/ns:service[@name="fileservice"]', namespaces=NS)[0]
    globus_service = fileservice.findall('ns:service[@serviceType="Globus"]', namespaces=NS)
    if globus_service:
        base = globus_service[0].get('base')
        if base != globus_base:
            print 'A base attribute of the Globus service in %s is\n'\
                  '%s which does not match\n'\
                  '%s set in %s.' % (catalog_file, base, globus_base, os.environ['ESGINI'])
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
        datasets = root.xpath('/ns:catalog/ns:dataset/ns:dataset', namespaces=NS)
        for dataset in datasets:
            gridftp_access = dataset.findall('ns:access[@serviceName="GRIDFTP"]', namespaces=NS)[0]
            url_path = gridftp_access.get('urlPath')
            if url_path.startswith('/'):
                url_path = url_path[1:]
            SE(dataset, 'access', serviceName='Globus', urlPath=url_path)
        doc.write(catalog_path, xml_declaration=True, encoding='UTF-8', pretty_print=True)


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
                    print 'Done'
                    break
    else:
        service = SE(fileservice, 'service', base=globus_base, desc="Globus Transfer Service", name="Globus", serviceType="Globus")
        SE(service, 'property', name='requires_authorization', value='false')
        SE(service, 'property', name='application', value='Web Browser')
        doc.write(catalog_up, xml_declaration=True, encoding='UTF-8', pretty_print=True)


    # Process all xml files listed in /esg/content/thredds/esgcet/catalog.xml
    catalog = os.path.join(thredds_root, 'catalog.xml')
    parser = XMLParser(remove_blank_text=True)
    doc = parse(catalog, parser)
    root = doc.getroot()
    catalog_ref = root.xpath('/ns:catalog/ns:catalogRef', namespaces=NS)
    catalog_files = []
    for cr in catalog_ref:
        href = cr.get('{%s}href' % XLINK)
        catalog_files.append(href)
    print 'Found %d catalog files to process' % len(catalog_files)
    for catalog_file in catalog_files:
        catalog_path = os.path.join(thredds_root, catalog_file)
        print 'Processing %s' % catalog_path
        add_globus(catalog_path, globus_base)

    # re-initialize the THREDDS server
    print "Reinitializing THREDDS server"
    thredds.reinitializeThredds()

    # re-harvest all catalogs
    print "Re-harvesting all catalogs" 
    for catalog_file in catalog_files:
        catalog_url = thredds_url + '/' + catalog_file
        harvest(catalog_url, esgf_harvesting_service_url, hessian_service_certfile)


def harvest(catalog_url, esgf_harvesting_service_url, hessian_service_certfile):

    print 'Harvesting catalog: %s' % catalog_url
    command = " ".join(['wget', 
                       '--no-check-certificate',
                       '--ca-certificate %s' % hessian_service_certfile,
                       '--certificate %s' % hessian_service_certfile,
                       '--private-key %s' % hessian_service_certfile,
                       '--verbose',
                       '--post-data="uri=%s&metadataRepositoryType=THREDDS"' % catalog_url,
                       ' %s' % esgf_harvesting_service_url])
    print 'Executing command: %s' % command
    os.system(command)


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
          'looking for datasets that were published without Globus file service and add\n'\
          'Globus access to the datasets. If a dataset was published with Globus file\n'\
          'service configured, the script skip such a dataset leaving a corresponding xml\n'\
          'file unmodified. The script reinitializes THREDDS and requests Solr to reindex\n'\
          'the updated xml files. Because Hessian service requires SSL authentication, '\
          'the X.509 certificate, %s,\n'\
          'should be valid and requested by a user who has the publisher role in all\n'\
          'projects.\n'\
          'It is strongly advised that you make a copy of the entire %s\n'\
          'directory prior to running this script.' % (hessian_service_certificate, thredds_root_up, thredds_root_up)

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
