"""Raw data collector for Coverage."""

import sys
import re
import threading
import pymongo
import yaml

class PyTracer(object):

    def __init__(self, dbhost="localhost", dbport=27017, ignore_re=[]):
        self.data = {}
        self.should_trace_cache = {}
        self.cur_file_data = None
        self.cur_file_name = None
        self.last_line = 0
        self.data_stack = []
        self.last_exc_back = None
        self.last_exc_firstlineno = 0
        self.ignore_re = ignore_re
        try:
            self.con = pymongo.connection.Connection(dbhost, dbport)
            self.db = pymongo.database.Database(self.con, "coverage")
        except:
            self.con = None
            self.db = None

    def _trace(self, frame, event, arg_unused):
        """The trace function passed to sys.settrace."""

#        sys.stderr.write("trace event: %s %r @%d\n" % (event, frame.f_code.co_filename, frame.f_lineno))

        if self.last_exc_back:
            if frame == self.last_exc_back:
                self.cur_file_data, self.last_line = self.data_stack.pop()
            self.last_exc_back = None

        if event == 'call':
            # Entering a new function context.  Decide if we should trace
            # in this file.
            self.data_stack.append((self.cur_file_data, self.cur_file_name, self.last_line))
            filename = frame.f_code.co_filename
            tracename = self.should_trace_cache.get(filename)
            if tracename is None:
                tracename = self.should_trace(filename)
                self.should_trace_cache[filename] = tracename
            #print("called, stack is %d deep, tracename is %r" % (
            #               len(self.data_stack), tracename))
            if tracename:
                if tracename not in self.data:
                    self.data[tracename] = {}
                self.cur_file_data = self.data[tracename]
                self.cur_file_name = tracename
            else:
                self.cur_file_data = None
                self.cur_file_name = None
            # Set the last_line to -1 because the next arc will be entering a
            # code block, indicated by (-1, n).
            self.last_line = -1
        elif event == 'line':
            # Record an executed line.
            if self.cur_file_data is not None and self.cur_file_name:
                if not frame.f_lineno in self.cur_file_data:
                    self.cur_file_data[frame.f_lineno] = None
                    if self.cur_file_name.startswith("/") and self.db:
                        try:
                            self.db.lines.insert({"file": self.cur_file_name, "lines": [frame.f_lineno]})
                        except:
                            pass
#                        sys.stderr.write("%s %d\n" % (self.cur_file_name, frame.f_lineno))
            self.last_line = frame.f_lineno
        elif event == 'return':
            self.cur_file_data, self.cur_file_name, self.last_line = self.data_stack.pop()
            #print("returned, stack is %d deep" % (len(self.data_stack)))
        elif event == 'exception':
            #print("exc", self.last_line, frame.f_lineno)
            self.last_exc_back = frame.f_back
            self.last_exc_firstlineno = frame.f_code.co_firstlineno
        return self._trace

    def start(self):
        """Start this Tracer.

        Return a Python function suitable for use with sys.settrace().

        """
        sys.settrace(self._trace)
        return self._trace

    def stop(self):
        """Stop this Tracer."""
        sys.settrace(None)

    def get_stats(self):
        """Return a dictionary of statistics, or None."""
        return None

    def should_trace(self, filename):
        res = True
        for regexp in self.ignore_re:
            if regexp.match(filename):
                res = False
                break
        if res:
            return filename
        else:
            return False


class Collector(object):
    # The stack of active Collectors.  Collectors are added here when started,
    # and popped when stopped.  Collectors on the stack are paused when not
    # the top, and resumed when they become the top again.

    def __init__(self):
        self.tracers = []
        self._trace_class = PyTracer
        self.dbhost = "localhost"
        self.dbport = 27017
        ignore = []
        self.ignore_re = []
        try:
            fd = open("/etc/moncov.yaml", "r")
            params = yaml.load(fd.read())
            self.dbhost = params["dbhost"]
            self.dbport = params["dbport"]
            ignore = params["ignore"]
        except:
            pass
        for pattern in ignore:
            self.ignore_re.append(re.compile(pattern))


    def __repr__(self):
        return "<Collector at 0x%x>" % id(self)

    def _start_tracer(self):
        """Start a new Tracer object, and store it in self.tracers."""
        tracer = PyTracer(self.dbhost, self.dbport, self.ignore_re)
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
