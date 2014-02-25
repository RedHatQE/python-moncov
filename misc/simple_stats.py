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
cursor=list(db.lines.find())
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
    lines = set(map(lambda number: int(number), doc['lines']))
    total, hits = reduce( \
        lambda r, x: (r[0] + 1, r[1] + (x.lineno in lines and 1 or 0)), \
        filter(lambda x: hasattr(x, "lineno"), ast.walk(tree)), \
        (0, 0) \
    )
    if total == 0:
        print "...empty"
        continue
    print ": %1.2f" % (float(hits)/float(total))
