Python code coverage measurement tool
=====================================
#### Remote python (t)racer pushing results to a MongoDB

Usage
-----

* pip install moncov
* check /etc/moncov.yaml
* moncov reset
* sudo moncov enable 
* python misc/sample.py
* sudo moncov disable
* moncov update
* moncov simple | grep sample

Hints
-----
* `events_count in /etc/moncov.yaml` can be adjusted to reduce record drops
* `moncov update -s` forks a daemon that updates the stats each -t seconds
* use `moncov simple_xml -o coverage.xml` to feed cobertura and alike


Notes
-----
* branch rates are a work-in-progress
* in case of a race condition:
* loosing line events is OK
* double-counting line events is bad
* moncov reset creates a custom pivot to prevent double counting
* some events might be lost because of the custom pivot election
