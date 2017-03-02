myproxy-logon -s pcmdi.llnl.gov -l sashakames -o ~/.globus/certificate-file
wget --no-check-certificate --ca-certificate /export/ames4/.globus/certificate-file --certificate /export/ames4/.globus/certificate-file --private-key /export/ames4/.globus/certificate-file --verbose --post-file=update.xml 'https://pcmdi.llnl.gov/esg-search/ws/update'
