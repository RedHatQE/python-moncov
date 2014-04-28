import yaml
import logging
import re
import pymongo

_DBCACHE = {}

log = logging.getLogger(__name__)

try:
    with open('/etc/moncov.yaml') as fd:
        CFG = yaml.load(fd.read())
except Exception as e:
    log.warning("can't read config: %s" % e.message)
    CFG = {}

DBHOST = CFG.get('dbhost', 'localhost')
DBPORT = CFG.get('dbport', 27017)
DBNAME = CFG.get('dbname', 'moncov')
EVENTS_COUNT = CFG.get('events_count', 8192)
EVENTS_TOTALSIZE = CFG.get('events_totalsize', EVENTS_COUNT * 1024)

try:
    WHITELIST = map(lambda item: re.compile(item), CFG.get('whitelist', ['.*']))
except Exception as e:
    log.warning("can't process whitelist, using: ['.*']; %s" % e.message)
    WHITELIST = [re.compile('.*')]
try:
    BLACKLIST = map(lambda item: re.compile(item), CFG.get('blacklist', []))
except Exception as e:
    log.warning("can't process blacklist, using: []; %s" % e.message)
    BLACKLIST = []

def get_connection(dbhost=DBHOST, dbport=DBPORT):
    if (dbhost, dbport) not in _DBCACHE:
        _DBCACHE[dbhost, dbport] = pymongo.mongo_client.MongoClient(dbhost, dbport)
    return _DBCACHE[dbhost, dbport]

def get_db(dbhost=DBHOST, dbport=DBPORT, dbname=DBNAME):
    if (dbhost, dbport, dbname) not in _DBCACHE:
        _DBCACHE[dbhost, dbport, dbname] = get_connection(dbhost, dbport)[dbname]
    return _DBCACHE[dbhost, dbport, dbname]

def get_dbdetails(db=None):
    '''return dbhostname, dbport, dbname'''
    if db is None:
        return DBHOST, DBPORT, DBNAME
    return db.connection.host, db.connection.port, db.name

def get_relist(relist):
    if type(relist) is not list:
        relist = relist.split(',')
    return [re.compile(item) for item in relist]

def get_whitelist(whitelist=None):
    if whitelist is None:
        return WHITELIST
    return get_relist(whitelist)


def get_blacklist(blacklist=None):
    if blacklist is None:
        return BLACKLIST
    return get_relist(blacklist)
