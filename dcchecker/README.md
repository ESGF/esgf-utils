Dataset Count Checker v1.00
============================
For installation instructions, refer to 'INSTALL'.

Usage notes
===========
1. The installer installs a cron that launches the tests once every six hours.
Change the /etc/cron.d/checkdscount if you want to change frequency.

2. The minute value in the cron is chosen in a pseudo-random fashion to try and 
ensure that all sites running the checks don't end up firing queries at the same time.

3. There can be transient issues; nodes going through a service restart or flaky
network conditions that might sometimes cause numbers to fluctuate; it is to be expected.

4. If you consistently see what you believe to be a incorrect count from a node (use discretion), you may want to inform the concerned node admin/list.

5. The script, after each run, gives the diff against the reference file, which start with 'old' in the filenames; these are by design not automatically updated, so as to give you an opportunity
to review the changes and decide what's a temporary change and what's a permanent one, and update the 'old' files according, manually.

Wishlist for next release
=========================
1. Make the output available on the web for browser/API queries.


