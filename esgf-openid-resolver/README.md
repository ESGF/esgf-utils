ESGF Openid Resolver
=====================
This tool uses code from the following projects.
1. Stephen Pascoe's esgf-pyclient 
https://github.com/stephenpascoe/esgf-pyclient.git) 
2. python-openid
https://github.com/openid/python-openid.git

Install Prerequisites
======================
python-setuptools, pip, python-lxml, argparse.
It's recommened to first setup python-setuptools and python-lxml using apt-get/yum.
Next, install pip using easy_install and finally, install argparse, using pip.


Quick Installation
==================
1. Install the egg file for esgf-pyclient
2. Install the egg file for the modified python-openid
3. Place the files oidtoemail.py and esgf-ca-bundle.crt in the same directory.

Installation from Source
=========================
1. Clone esgf-pyclient from https://github.com/stephenpascoe/esgf-pyclient.git and install it.
2. Clone python-openid from https://github.com/openid/python-openid.git
3. Checkout commit id b1d37696469921f1025395201864842427fc32fb
4. Apply the patch provided here (python-openid-allow-optional-flags-to-libcurl.patch) using git-am.
5. Install the patched python-openid


Usage
======
oidtoemail.py can accept either a single openid string or a file containing several openids to resolve. To pass a file as argument, use the '--file' flag.
eg: python oidtoemail.py 'https://esg-dn1.nsc.liu.se/esgf-idp/openid/pchengi' 
Contact 'esg-admin' at 'nsc.liu.se' for queries/support.

CEDA Openids
============
The Openid service at CEDA requires that you seek prior approval in order to query it. The DN of the machine from which the query would be fired needs to be registered with them. Contact 'philip.kershaw' at 'stfc.ac.uk' for this. Once this registration is done, replace the value of '/test/test' with the actual DN in the line that says 'QUERY_ISSUER' in oidtoemail.py.
