misc tools
==========

ESGF utilities for war packaging and certificate signing.

Contents
=========
1. packagedists.sh: script to package wars.  Don't change the version number in the esg-node script in the esgf-installer repo! Remember to specify the correct version in the first three lines of the packagedists.sh script.
2. signcerts.tgz: utility scripts to sign CSRs for ESGF. untar with tar -xvzf -C /root to ensure it's extracted into the correct directory. Also put your CA passphrase in the /root/scripts/capass file. Refer to the README file in the tarball for more details.
