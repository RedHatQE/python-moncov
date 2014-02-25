#!/usr/bin/python

import pymongo
import ast
import sys
import yaml

try:
    with open('/etc/moncov.yaml') as fd:
        config = yaml.load(fd.read())
except Exception as e:
    print "# can't read config file /etc/moncov.yaml: %s" % e.message
    print "# using default config"
    config = {}

host = config.get('dbhost', 'localhost')
port = config.get('dbport', 27017)

try:
    connection=pymongo.connection.Connection(host=host, port=port)
except Exception as e:
    print "# connection error: %s" % e.message
    sys.exit(2)

db=pymongo.database.Database(connection, "moncov")
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
    total_set = reduce( \
        lambda result, x: result | set([x.lineno]), \
        filter(lambda x: hasattr(x, "lineno"), ast.walk(tree)), \
        set() \
    )
    total = len(total_set)
    hits = len(total_set & hit_lines)
    if total == 0:
        print "...empty"
        continue
    print ": %1.2f (%s/%s)" % (float(hits)/float(total), hits, total)
