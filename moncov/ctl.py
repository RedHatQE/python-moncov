import conf
import logging
log = logging.getLogger(__name__)

SITE_FILENAME='z_moncov.pth'

def disable():
    '''disable coverage collecting'''
    import sys
    sys.settrace(None)


def enable(db=None, dbhost=conf.DBHOST, dbport=conf.DBPORT, dbname=conf.DBNAME,
        whitelist=conf.WHITELIST, blacklist=conf.BLACKLIST):
    '''enable coverage collecting'''
    import collector
    c = collector.Collector(db=db, dbhost=dbhost, dbport=dbport, dbname=dbname,
            whitelist=whitelist, blacklist=blacklist)
    c.start()
    return c


def drop(db=None, host=conf.DBHOST, port=conf.DBPORT, name=conf.DBNAME):
    '''drop the coverage db'''
    try:
        if db is None:
            db = conf.get_db(host, port, name)
    except Exception as e:
        log.warning("couldn't get db %r, %r, %r: %r" % (host, port, name, e.message))
    else:
        try:
            db.connection.drop_database(db)
        except Exception as e:
            log.warning('failed to drop %r: %r' % (db, e.message))
        else:
            log.info("dropped: %r" % db)

def init(db=None, dbhost=conf.DBHOST, dbport=conf.DBPORT, dbname=conf.DBNAME,
        events_count=conf.EVENTS_COUNT, events_totalsize=conf.EVENTS_TOTALSIZE):
    '''initialize necessary events collection'''        # uses 2 collections
    # - lines: indexed by filename,lineno; fields: hits count
    # - events: capped collection for short-term filename,lineno events
    #           storage
    # events is map-reduced to lines with the moncov stats commands
    if db is None:
        db = conf.get_db(dbhost=dbhost, dbport=dbport, dbname=dbname)
    import pymongo
    try:
        db.create_collection(name="events", capped=True, max=events_count,
                            size=events_totalsize)
        pivot = {'event_id': pymongo.helpers.bson.ObjectId()}
        db.last_event.insert(pivot)
    except pymongo.errors.CollectionInvalid as e:
        # already has such collection; ok
        log.info("Events collection already present in %r: %r" % (db, e))
    return db

def get_collecting_code(dbhost, dbport, dbname, whitelist, blacklist):
    '''return the code to use for coverage collecting initialization from a pth file'''
    whitelist = map(lambda regexp: type(regexp) is str and regexp or regexp.pattern, whitelist)
    blacklist = map(lambda regexp: type(regexp) is str and regexp or regexp.pattern, blacklist)
    return 'import moncov; c = moncov.Collector(dbhost=%r, dbport=%r, dbname=%r, whitelist=%r, blacklist=%r); c.start()\n' % \
        (dbhost, dbport, dbname, whitelist, blacklist)

def sys_enable(db=None, dbhost=conf.DBHOST, dbport=conf.DBPORT, dbname=conf.DBNAME, whitelist=conf.WHITELIST, blacklist=conf.BLACKLIST):
    '''enable system-wide coverage stats collecting; requires permissions'''
    if db is not None:
        # convert to connection/port/name
        host, port, name = db.connection.host, db.connection.port, db.name
    code = get_collecting_code(dbhost=dbhost, dbport=dbport, dbname=dbname,
                            whitelist=whitelist, blacklist=blacklist)
    log.debug("code to use: %r" % code)
    import os
    import site
    import re
    # FIXME: implement with setup??
    filename = os.path.join(site.getsitepackages()[1], SITE_FILENAME)
    try:
        with open(filename, 'w+') as fd:
            fd.write(code)
    except Exception as e:
        log.warning("couldn't dump code to %s: %r" % (filename, e))
    else:
        log.info('written: %s' % filename)

def sys_disable(*args, **kvs):
    '''disable system-wide coverage stats collecting'''
    import site
    import os
    filename = os.path.join(site.getsitepackages()[1], SITE_FILENAME)
    # FIXME: implement with setup??
    try:
        os.unlink(filename)
    except Exception as e:
       log.warning("couldn't remove file %s: %r" % (filename, e))
    else:
        log.info('removed: %s' % filename)
