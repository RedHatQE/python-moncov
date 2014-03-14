import moncov
import pymongo
import logging
log = logging.getLogger(__name__)

#  => {_id: {file: <path>, line: <lineno>}, value: <hit-count>}
_MAP = '''function(){emit({file: this.file, line: this.line}, 1)}'''

# {_id: {file: <path>, line: <lineno>}, value: <hit-count>}
# sum per hit-counts
_REDUCE = '''function(key, values){return Array.sum(values)}'''


def update(db=None, dbhost=moncov.conf.DBHOST, dbport=moncov.conf.DBPORT,
            dbname=moncov.conf.DBNAME):
    '''map-reduce events to lines collection'''
    if db is None:
        db = moncov.conf.get_db(dbhost=dbhost, dbport=dbport, dbname=dbname)
    # uses 2 collections
    # - lines: indexed by filename,lineno; fields: value: hit-count
    # - events: capped collection for short-term filename,lineno events
    # ensure proper index by _id.file, _id.line
    db.lines.ensure_index([('_id.file', pymongo.ASCENDING), ('_id.line', pymongo.ASCENDING)],
            unique=True, drop_dups=True, sparse=True)
    try:
        pivot = db.last_event.find({}, sort=[('$natural', 1)], limit=1)[0]
    except IndexError as e:
        # init not yet called
        return
 
    # figure out the last used _id to avoid double-counting
    # - the pivot: no records newer than pivot are being counted
    # after the test&set succeeded
    try:
        last_event = db.events.find({}, sort=[('$natural', -1)], limit=1)[0]
    except IndexError as e:
        # no events to count
        return
    original_last = db.last_event.find_and_modify({'event_id': pivot['event_id']},
            update={'event_id': last_event['_id']})
    # limit the counting with map-reduce query based on the last_event._id
    if original_last is None:
        # race detected --- some other process already counted the interval
        return
    else:
        # will limit the map-reduce to id newer than original
        # last.event_id
        query = {'_id': {'$gt': original_last['event_id'], '$lte': last_event['_id']}}
    # update the hit-counts, "merge-back" with reduce
    response = db.events.map_reduce(map=_MAP, reduce=_REDUCE, query=query,
            out={'reduce': 'lines'}, full_response=True)
    log.info(response)
    #import pprint
    #print pprint.pformat(response)

if __name__ == '__main__':
    update()
