# dataset-url-mapper

Examples of mapping datasets to files (this procedure retrieves file urls and converts to physical paths).  We provide a single command line script example: map_files.py

## Requirements

requests

## usage examples

**CMIP5 example:**

> $ python map_files.py 'cmip5.output1.CMCC.CMCC-CM.historical.day.atmos.day.r1i1p1.v20120514|aims3.llnl.gov'

**CMIP6 exmaple:**

> $ python map_files.py 'CMIP6.CMIP.NASA-GISS.GISS-E2-1-G.historical.r1i1p1f1.3hr.clt.gn.v20181015|aims3.llnl.gov'

The output will contain test dataset root 'prefixes' in the paths.  Please replace the example mapping table with the actual roots when use with testing actual files.

