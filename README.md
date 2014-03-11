Python code coverage measurement tool
=====================================
#### Remote python (t)racer pushing results to a MongoDB

Usage
-----

* pip install moncov
* check /etc/moncov.yaml
* moncov update
* sudo moncov enable 
* python misc/sample.py
* sudo moncov disable
* moncov update
* moncov simple | grep sample

Notes
-----
* works in an best-effort service way
* loosing line events is OK
* double-counting line events is bad
* moncov update creates a custom pivot to guard double counting
* when run for the first time (or after moncov drop) some events might be lost
* systemd service present: moncov.service
* rpm spec file present
