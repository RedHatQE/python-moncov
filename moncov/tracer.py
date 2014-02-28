'''raw data tracer for Coverage'''
import sys
import pymongo

_CACHE = {}
_SHOULD_TRACE = {}

class PyTracer(object):
    def __init__(self, dbhost="localhost", dbport=27017, dbname='moncov', blacklist=[], whitelist=[]):
        self.blacklist = blacklist
        self.whitelist = whitelist
        self._cache = getattr(sys.modules[__name__], '_CACHE')
        self._should_process = getattr(sys.modules[__name__], '_SHOULD_TRACE')
        try:
            self.con = pymongo.connection.Connection(dbhost, dbport)
            self.db = pymongo.database.Database(self.con, dbname)
            self.db.lines.create_index([("file", pymongo.ASCENDING), ("line", pymongo.ASCENDING)], unique=True, drop_dups=True, sparse=True)
        except:
            self.con = None
            self.db = None
            self.enabled = False
        else:
            self.enabled = True

    def _trace(self, frame, event, arg_unused):
        """The trace function passed to sys.settrace."""
        # reentrance not allowed
        if not self.enabled or not self.db:
            return self._trace

        if event != 'line':
            # oly care about line events
            return self._trace

        filename, lineno = frame.f_code.co_filename, frame.f_lineno

        # needs processing?
        if filename not in self._should_process:
            # on black list?
            self.enabled = False # causes a call --- mask out
            self._should_process[filename] = \
                any([regexp.match(filename) for regexp in self.whitelist]) and \
                not any([regexp.match(filename) for regexp in self.blacklist])
            self.enabled = True

        if not self._should_process[filename]:
            return self._trace

        if (filename, lineno) in self._cache:
            # already reported --- don't care
            return self._trace

        # not yet collected
        try:
            self.enabled = False # causes a call
            self.db.lines.update({"file": filename, "line": lineno}, {'$setOnInsert': {}}, upsert=True, w=0)
        except:
            pass
        else:
            # remote cache synced; avoid reporting same (file, line) again
            self._cache[(filename, lineno)] = True
        finally:
            self.enabled = True

        return self._trace

    def start(self):
        """Start this Tracer."""
        self.enabled = True
        sys.settrace(self._trace)
        return self._trace

    def stop(self):
        """Stop this Tracer."""
        self.enabled = False
        sys.settrace(None)

    def get_stats(self):
        """Return a dictionary of statistics, or None."""
        return None


