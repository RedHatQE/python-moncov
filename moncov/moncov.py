"""Raw data collector for Coverage."""

import sys
import re
import threading
import pymongo
import yaml
import conf

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


class Collector(object):
    # The stack of active Collectors.  Collectors are added here when started,
    # and popped when stopped.  Collectors on the stack are paused when not
    # the top, and resumed when they become the top again.

    def __init__(self):
        self.tracers = []
        self._trace_class = PyTracer
        from conf import (DBHOST, DBPORT, DBNAME, BLACKLIST, WHITELIST)
        self.dbhost = DBHOST
        self.dbport = DBPORT
        self.dbname = DBNAME
        self.blacklist = BLACKLIST
        self.whitelist = WHITELIST


    def __repr__(self):
        return "<Collector at 0x%x>" % id(self)

    def _start_tracer(self):
        """Start a new Tracer object, and store it in self.tracers."""
        tracer = PyTracer(self.dbhost, self.dbport, self.dbname, self.blacklist, self.whitelist)
        fn = tracer.start()
        self.tracers.append(tracer)
        return fn

    # The trace function has to be set individually on each thread before
    # execution begins.  Ironically, the only support the threading module has
    # for running code before the thread main is the tracing function.  So we
    # install this as a trace function, and the first time it's called, it does
    # the real trace installation.

    def _installation_trace(self, frame_unused, event_unused, arg_unused):
        """Called on new threads, installs the real tracer."""
        # Remove ourselves as the trace function
        sys.settrace(None)
        # Install the real tracer.
        fn = self._start_tracer()
        # Invoke the real trace function with the current event, to be sure
        # not to lose an event.
        if fn:
            fn = fn(frame_unused, event_unused, arg_unused)
        # Return the new trace function to continue tracing in this scope.
        return fn

    def start(self):
        """Start collecting trace information."""

        # Check to see whether we had a fullcoverage tracer installed.
        traces0 = []
        if hasattr(sys, "gettrace"):
            fn0 = sys.gettrace()
            if fn0:
                tracer0 = getattr(fn0, '__self__', None)
                if tracer0:
                    traces0 = getattr(tracer0, 'traces', [])

        # Install the tracer on this thread.
        fn = self._start_tracer()

        for args in traces0:
            (frame, event, arg), lineno = args
            try:
                fn(frame, event, arg, lineno=lineno)
            except TypeError:
                raise Exception(
                    "fullcoverage must be run with the C trace function."
                )

        # Install our installation tracer in threading, to jump start other
        # threads.
        threading.settrace(self._installation_trace)
