Python code coverage measurement tool
=====================================

Simple python tracer (based on python-coverage code) pushing result to MongoDB

Usage
-----

* yum install python-moncov
* check /etc/moncov.yaml
* systemctl start moncov.service
* python misc/sample.py
* systemctl stop moncov.service
* python misc/simple_stats.py | grep sample
