'''raw data tracer for Coverage'''
import sys
import threading
import logging
log = logging.getLogger(__name__)

_SHOULD_TRACE = {}

class PyTracer(object):
    def __init__(self, dbhost="localhost", dbport=27017, dbname='moncov', blacklist=[], whitelist=[]):
        self.blacklist = blacklist
        self.whitelist = whitelist
        self._should_process = getattr(sys.modules[__name__], '_SHOULD_TRACE')
        # a stack of line lists for caching inserts of executed lines
        self.stack = [[]]
        # uses 2 collections
        # - lines: indexed by filename,lineno; fields: hits count
        # - events: capped collection for short-term filename,lineno events
        #           storage
        # events is map-reduced to lines with the moncov stats commands
        try:
            import ctl
            self.db = ctl.init(dbhost=dbhost, dbport=dbport, dbname=dbname)
        except Exception as e:
            print >> sys.stderr, "%r, %r error: %r" % (__file__, self, e)
            self.con = None
            self.db = None
            self.enabled = False
            return
        else:
            self.enabled = True
        log.info('%r using: %r' % (self, self.db))


    def _trace(self, frame, event, arg_unused):
        """The trace function passed to sys.settrace."""
        # reentrance not allowed
        if not self.enabled or not self.db:
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

        if event == 'call':
            # push new frame line insert list
            self.stack.append([{'file': filename, 'line': lineno}])
            return self._trace

        if event == 'return' or event == 'exception':
            # commit changes for current frame
            if not self.stack:
                return self._trace
            self.enabled = False # causes calls
            lines = self.stack.pop()
            if not lines:
                self.enabled = True
                return self._trace
            try:
                self.db.events.insert(lines, w=0)
            except Exception as e:
                print >> sys.stderr, "%r, %r error: %r" % (__file__, self, e)
            finally:
                self.enabled = True
            if event == 'exception':
                self.stack.append([])
            return self._trace

        if event != 'line':
            # c_* events not processed
            return self._trace

        # add filename,lineno to processing list
        self.stack[-1].append({"file": filename, "line": lineno})
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


