====================
Simple funkLoad test
====================

This is a simple funkLoad testcase.

You need to install funkload (can be done e.g. with pip) and gnuplot (via your
package manager) if you want to create plots. It requires a running web test
server (you can edit which one in the .conf file)

WARNING: You should *not* run this script against a server that is not under
your responsablity as it can result a DOS in bench mode.

For more information on configuration, options, etc. refer to the funkload
documentation page: http://funkload.nuxeo.org



Instruction
-----------

1/ Bench it

   Bench it with few cycles::

     fl-run-bench test_Simple.py Simple.test_simple

   Note that for correct interpretation you should run the FunkLoad bencher
   in a different host than the server, the server should be 100% dedicated
   to the application.

   If you want to bench with more than 200 users, you need to reduce the
   default stack size used by a thread, for example try a `ulimit -s 2048`
   before running the bench.

   Performance limits are hit by FunkLoad before apache's limit is reached,
   since it uses significant CPU resources.

2/ Build the report::

   fl-build-report --html simple-bench.xml
