#!/usr/bin/python

import pymongo
import ast
import sys
import moncov

# prevent tracing ourselves
moncov.ctl.disable()


try:
    connection=pymongo.connection.Connection(host=moncov.conf.DBHOST, port=moncov.conf.DBPORT)
except Exception as e:
    print "# connection error: %s" % e.message
    sys.exit(2)

db=pymongo.database.Database(connection, moncov.conf.DBNAME)
cursor_grouped = db.lines.aggregate([{"$group": {"_id": "$file", "lines": {"$addToSet": "$line"}}}])

for doc in cursor_grouped['result']:
    filename = doc['_id']
    print "%s" % filename,
    if str(filename).startswith('<'):
        print "...not a *.py file"
        continue
    try:
        with open(filename) as fd:
            src = fd.read()
    except Exception as e:
        print "...can't read file: %s" % e.message
        continue
    try:
        tree = ast.parse(src)
    except Exception as e:
        print "...has syntax errors: %s" % e.message
	continue
    hit_lines = set(map(lambda number: int(number), doc['lines']))
    total_set = set([x.lineno for x in ast.walk(tree) if hasattr(x, 'lineno')])
    total = len(total_set)
    hits = len(total_set & hit_lines)
    if total == 0:
        print "...empty"
        continue
    print ": %1.2f (%s/%s)" % (float(hits)/float(total), hits, total)
