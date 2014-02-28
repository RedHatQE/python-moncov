# prevent tracing ourselves
import moncov; moncov.ctl.disable()
import ast
import sys


def print_stats(db=None, whitelist=None, blacklist=None):
    if db is None:
        db = moncov.conf.get_db()
    whitelist = moncov.conf.get_whitelist(whitelist)
    blacklist = moncov.conf.get_blacklist(blacklist)
    cursor_grouped = db.lines.aggregate([{"$group": {"_id": "$file", "lines": {"$addToSet": "$line"}}}])
    for doc in cursor_grouped['result']:
        filename = doc['_id']
        if not any([lambda pattern: pattern.match(filename) for pattern in whitelist]) or \
                any([lambda pattern: pattern.match(filename) for pattern in blacklist])
            continue
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
