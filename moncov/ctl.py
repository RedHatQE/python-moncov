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
        log.warning("couldn't get db %r, %r, %r: %r" % (host, port, name, e))
    else:
        try:
            db.flushdb()
        except Exception as e:
            log.warning('failed to drop %r: %r' % (db, e))
        else:
            log.info("dropped: %r" % db)

def init(db=None, dbhost=conf.DBHOST, dbport=conf.DBPORT, dbname=conf.DBNAME):
    '''initialize necessary events collection'''
    if db is None:
        db = conf.get_db(dbhost=dbhost, dbport=dbport, dbname=dbname)
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
        dbhost, dbport, dbname = conf.get_dbdetails(db)
    code = get_collecting_code(dbhost=dbhost, dbport=dbport, dbname=dbname,
                            whitelist=whitelist, blacklist=blacklist)
    log.debug("code to use: %r" % code)
    import os
    from distutils import sysconfig
    import re
    # FIXME: implement with setup??
    filename = os.path.join(sysconfig.get_python_lib(), SITE_FILENAME)
    try:
        with open(filename, 'w+') as fd:
            fd.write(code)
    except Exception as e:
        log.warning("couldn't dump code to %s: %r" % (filename, e))
    else:
        log.info('written: %s' % filename)

def sys_disable(*args, **kvs):
    '''disable system-wide coverage stats collecting'''
    import os
    from distutils import sysconfig
    filename = os.path.join(sysconfig.get_python_lib(), SITE_FILENAME)
    # FIXME: implement with setup??
    try:
        os.unlink(filename)
    except Exception as e:
       log.warning("couldn't remove file %s: %r" % (filename, e))
    else:
        log.info('removed: %s' % filename)
