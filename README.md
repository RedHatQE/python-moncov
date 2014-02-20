Python code coverage measurement tool
=====================================

Simple python tracer (based on python-coverage code) pushing result to MongoDB

Usage
-----

* yum install python-moncov
* systemctl start moncov.service
* python \<test.py\>
* systemctl stop moncov.service
* mongo
* use moncov
* db.lines.find()
