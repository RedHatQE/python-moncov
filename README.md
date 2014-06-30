Python code coverage measurement tool
=====================================
#### Remote python (t)racer pushing results to a redis store

Usage
-----

* pip install moncov
* check /etc/moncov.yaml
* moncov reset
* sudo moncov enable 
* python misc/sample.py
* sudo moncov disable
* moncov simple | grep sample

Hints
-----
* use `moncov simple_xml -o coverage.xml` to feed cobertura and alike
* please, refer to [stack overflow] (http://stackoverflow.com/questions/15759150/src-lxml-etree-defs-h931-fatal-error-libxml-xmlversion-h-no-such-file-or-di) should pip install fail for you with `libxml/xmlversion.h: No such file or directory`


Notes
-----
* branch rates are a work-in-progress
