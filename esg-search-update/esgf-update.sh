#myproxy-logon -s pcmdi.llnl.gov -l sashakames -o ~/.globus/certificate-file
wget --no-check-certificate --ca-certificate /export/ames4/.globus/certificate-file --certificate /export/ames4/.globus/certificate-file --private-key /export/ames4/.globus/certificate-file --verbose --post-file=update-idx.xml 'https://esgf-node.llnl.gov/esg-search/ws/update'
