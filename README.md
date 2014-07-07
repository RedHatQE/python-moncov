Python code coverage measurement tool
=====================================
#### Remote python (t)racer pushing results to a redis store
#### and Ned Batchelder's coverage.py on-the-fly remote reports wrapper

Usage
-----

* pip install moncov
* check /etc/moncov.yaml
* moncov reset
* sudo moncov enable
* python misc/sample.py
* sudo moncov disable
* moncov ned --include "\*sample.py" --report

Hints
-----
* use `moncov simple_xml -o coverage.xml` to feed cobertura and alike
* please, refer to [stack overflow] (http://stackoverflow.com/questions/15759150/src-lxml-etree-defs-h931-fatal-error-libxml-xmlversion-h-no-such-file-or-di) should pip install fail for you with `libxml/xmlversion.h: No such file or directory`


Notes
-----
* coverage.py report options should match those of coverage.py
* esp. --xml, --annotate, --fail-under
* try moncov ned --help
