import yaml
import logging
import re
import redis

_DBCACHE = {}

log = logging.getLogger(__name__)

try:
    with open('/etc/moncov.yaml') as fd:
        CFG = yaml.load(fd.read())
except Exception as e:
    log.warning("can't read config: %s" % e)
    CFG = {}

DBHOST = CFG.get('dbhost', 'localhost')
DBPORT = CFG.get('dbport', 6379)
DBNAME = CFG.get('dbname', 0)

try:
    WHITELIST = map(lambda item: re.compile(item), CFG.get('whitelist', ['.*']))
except Exception as e:
    log.warning("can't process whitelist, using: ['.*']; %s" % e)
    WHITELIST = [re.compile('.*')]
try:
    BLACKLIST = map(lambda item: re.compile(item), CFG.get('blacklist', []))
except Exception as e:
    log.warning("can't process blacklist, using: []; %s" % e)
    BLACKLIST = []

def get_db(dbhost=DBHOST, dbport=DBPORT, dbname=DBNAME):
    if (dbhost, dbport, dbname) not in _DBCACHE:
        _DBCACHE[dbhost, dbport, dbname] = redis.StrictRedis(host=dbhost, port=dbport, db=dbname)
    return _DBCACHE[dbhost, dbport, dbname]

def get_dbdetails(db=None):
    '''return dbhostname, dbport, dbname'''
    if db is None:
        return DBHOST, DBPORT, DBNAME
    return db.connection_pool.get_connection('ping').host, \
            db.connection_pool.get_connection('ping').port, \
            db.connection_pool.get_connection('ping').db

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
