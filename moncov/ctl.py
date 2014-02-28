import conf
import logging
log = logging.getLogger(__name__)

SITE_FILENAME='z_moncov.pth'

def disable():
    '''disable coverage collecting'''
    import sys
    sys.settrace(None)


def enable():
    '''enable coverage collecting'''
    import moncov
    c = moncov.Collector()
    c.start()
 

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

def get_collecting_code(host, port, name, whitelist, blacklist):
    '''return the code to use for coverage collecting initialization from a pth file'''
    whitelist = map(lambda regexp: type(regexp) is str and regexp or regexp.pattern, whitelist)
    blacklist = map(lambda regexp: type(regexp) is str and regexp or regexp.pattern, blacklist)
    return 'import moncov; import re; c = moncov.Collector(host=%r, port=%r, name=%r, whitelist=%r, blacklist=%r); c.start()\n' % \
        (host, port, name, whitelist, blacklist)

def sys_enable(db=None, host=conf.DBHOST, port=conf.DBPORT, name=conf.DBNAME, whitelist=conf.WHITELIST, blacklist=conf.BLACKLIST):
    '''enable system-wide coverage stats collecting; requires permissions'''
    if db is not None:
        # convert to connection/port/name
        host, port, name = db.connection.host, db.connection.port, db.connection.name
    code = get_collecting_code(host, port, name, whitelist, blacklist) 
    log.debug("code to use: %r" % code)
    import os
    import site
    import re
    logging.basicConfig()
    # FIXME: implement with setup??
    filename = os.path.join(site.getsitepackages()[1], SITE_FILENAME)
    try:
        with open(filename, 'w+') as fd:
            fd.write(code)
    except Exception as e:
        log.warning("couldn't dump code to %s: %s" % (filename, e.message))
    else:
        log.info('written: %s' % filename)

def sys_disable(*args, **kvs):
    '''disable system-wide coverage stats collecting'''
    import site
    import os
    logging.basicConfig()
    filename = os.path.join(site.getsitepackages()[1], SITE_FILENAME)
    # FIXME: implement with setup??
    try:
        os.unlink(filename)
    except Exception as e:
       log.warning("couldn't remove file %s: %s" % (filename, e.message))
    else:
        log.info('removed: %s' % filename) 
