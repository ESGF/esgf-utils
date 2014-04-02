ESGF Openid Resolver
=====================
This tool uses code from the following projects, with minor modifications.
1. Stephen Pascoe's esgf-pyclient 
https://github.com/stephenpascoe/esgf-pyclient.git) 
2. python-openid
https://github.com/openid/python-openid.git

Quick Installation
==================
1. Install the egg file for the modifid esgf-pyclient
2. Install the egg file for the modified python-openid
3. Place the files oidtoemail.py and esgf-ca-bundle.crt in the same directory.

Installation from Source
=========================
1. Clone esgf-pyclient from https://github.com/stephenpascoe/esgf-pyclient.git
2. Checkout commit id 401ce2008a8f5f623acffda98348376ebc6d61d1
3. Apply the patch provided here (esgf-pyclient-get-issuer-from-user.patch)
4. Install the patched esgf-pyclient
5. Clone python-openid from https://github.com/openid/python-openid.git
6. Apply the patch provided here (python-openid-allow-optional-flags-to-libcurl.patch
7. Install the patched python-openid

Usage
======
oidtoemail.py can accept either a single openid string or a file containing several openids to resolve. To pass a file as argument, use the '--file' flag. 
Contact esg-admin@nsc.liu.se for queries/support.

