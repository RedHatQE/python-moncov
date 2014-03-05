Python code coverage measurement tool
=====================================

Simple python tracer (based on python-coverage code) pushing result to MongoDB

Usage
-----

* yum install python-moncov
* check /etc/moncov.yaml
* sudo systemctl start moncov.service 
* python misc/sample.py
* sudo systemctl stop moncov.service
* moncov simple | grep sample
