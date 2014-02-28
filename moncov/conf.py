import yaml
import logging
import re
import pymongo

logging.basicConfig()
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

def get_connection(host=DBHOST, port=DBPORT):
    return pymongo.connection.Connection(host, port)

def get_db(host=DBHOST, port=DBHOST, name=DBNAME):
    return pymongo.database.Database(get_connection(host, port), name)
