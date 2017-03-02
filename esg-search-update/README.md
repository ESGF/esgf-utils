This is a sample helper script for specific "atomic metadata updates"
to esg-search / SOLR.  In this case we are flagging a group of
datasets as latest=false.  For input4MIPs this is needed because the
project uses a custom "version" facet rather than esg-publisher assigned versioning.

 * Requires myproxy-logon

