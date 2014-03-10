# prevent tracing ourselves
import moncov; moncov.ctl.disable()
import pymongo

#  => {_id: {file: <path>, line: <lineno>}, value: <hit-count>}
_MAP = '''function(){emit({file: this.file, line: this.line}, 1)}'''

# {_id: {file: <path>, line: <lineno>}, value: <hit-count>}
# sum per hit-counts
_REDUCE = '''function(key, values){return Array.sum(values)}'''


def update(db=None):
    '''map-reduce events to lines collection'''
    if db is None:
        db = moncov.conf.get_db()
    # uses 2 collections
    # - lines: indexed by filename,lineno; fields: value: hit-count
    # - events: capped collection for short-term filename,lineno events
    # ensure proper index by _id.file, _id.line
    db.lines.ensure_index([('_id.file', pymongo.ASCENDING), ('_id.line', pymongo.ASCENDING)],
            unique=True, drop_dups=True, sparse=True)
    # figure out the last used _id to avoid double-counting
    # sort of a test&set
    last_event = db.events.find({}, sort=[('$natural', -1)], limit=1)[0]
    original_last = db.last_event.find_and_modify({}, update={'event_id':
        last_event['_id']}, upsert=True)
    # limit the counting with map-reduce query based on the last_event._id
    if original_last is None:
        # was empty
        query = {}
    else:
        # will limit the map-reduce to id newer than original
        # last.event_id
        query = {'$gt': {'_id': original_last['event_id']}}
    # update the hit-counts, "merge-back" with reduce
    db.events.map_reduce(map=_MAP, reduce=_REDUCE, query=query,
            out={'reduce': 'lines'})

if __name__ == '__main__':
    update()
