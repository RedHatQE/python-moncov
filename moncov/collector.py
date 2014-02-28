"""Raw data collector for Coverage."""

import sys
import threading
import conf
import re
from tracer import PyTracer


class Collector(object):
    # The stack of active Collectors.  Collectors are added here when started,
    # and popped when stopped.  Collectors on the stack are paused when not
    # the top, and resumed when they become the top again.

    def __init__(self, host=None, port=None, name=None, whitelist=None, blacklist=None):
        self.tracers = []
        self._trace_class = PyTracer
        from conf import (DBHOST, DBPORT, DBNAME, BLACKLIST, WHITELIST)
        self.dbhost = host or DBHOST
        self.dbport = port or DBPORT
        self.dbname = name or DBNAME
        self.blacklist = [re.compile(regexp) for regexp in blacklist] or BLACKLIST
        self.whitelist = [re.compile(regexp) for regexp in whitelist] or WHITELIST


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
