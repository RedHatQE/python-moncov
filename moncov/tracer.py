'''raw data tracer for Coverage'''
import sys
import threading
import logging
log = logging.getLogger(__name__)

_SHOULD_TRACE = {}

class PyTracer(object):

    def __init__(self, dbhost="localhost", dbport=6379, dbname=0, blacklist=[], whitelist=[]):
        self.blacklist = blacklist
        self.whitelist = whitelist
        self._should_process = getattr(sys.modules[__name__], '_SHOULD_TRACE')
        self.last_lineno = -1
        self.last_exc_back = None
        # contains a history of self.last_linenos
        self.stack = []
        try:
            import conf
            self.db = conf.get_db(dbhost, dbport, dbname)
            # create a redis pipeline. pipeline.execute() need not
            # be transactional --- all operations should be just increments
            self.pipeline = self.db.pipeline(transaction=False)
        except Exception as e:
            log.error("got: %r, disabling." % e)
            self.stop()
        else:
            self.enabled = True
            log.info('%r using: %r' % (self, self.pipeline))


    def _trace(self, frame, event, arg_unused):
        """The trace function passed to sys.settrace."""
        # reentrance not allowed
        if not self.enabled:
            return self._trace

        # does the event need processing?
        if event != 'line' and event != 'call' and event != 'return' and event != 'exception':
            return self._trace

        # fetch filename and line number from frame details
        filename, lineno = frame.f_code.co_filename, frame.f_lineno

        # does the filename need processing?
        # the result of blacklist/whitelist filtering is cached here
        # the cache is shared between all tracers of a process
        # the items in the cache stabilize
        # filename, if first encountered, is marked as being traced in redis, too
        # all (even remote) tracers have same white/black list
        # marking of the filenames will happen multiple times but we don't mind
        if filename not in self._should_process:
            # mask-out tracing
            self.enabled = False
            self._should_process[filename] = \
                any([regexp.match(filename) for regexp in self.whitelist]) and \
                not any([regexp.match(filename) for regexp in self.blacklist])
            if self._should_process[filename]:
                try:
                    # mark this filename being processed
                    # this might preempt self.pipeline from time to time
                    # we should be safe
                    self.db.sadd('filenames', filename)
                except Exception as e:
                    log and log.warning('%s._trace: marking %s traced got exception: %r' %  \
                        (self, filename, e))
            # un-mask tracing
            self.enabled = True
        if not self._should_process[filename]:
            # the filename doesn't need processing --- filtered out
            return self._trace

        if self.last_exc_back:
            # handling exc_back situation
            if frame == self.last_exc_back:
                # handling exception
                try:
                    # mask-out tracing
                    self.enabled = False
                    # record the line being executed
                    self.pipeline.zincrby(filename, str(self.last_lineno) + ',' + str(-self.last_exc_back.f_code.co_firstlineno), 1)
                    # flush what we've got and start catching events into pipeline again
                    # in case not all operations made it to the server, print a warning
                    if not all(self.pipeline.execute()):
                        log and log.warning('%s._trace: pipeline.execute missed events' % self)
                except Exception as e:
                    log and log.warning('%s._trace got error: %r' % (self, e))
                finally:
                    # un-mask tracing
                    self.enabled = True
                    self.last_lineno = self.stack.pop()
            self.last_exc_back = None


        # process the event
        if event == 'call':
            self.stack.append(self.last_lineno)
            self.last_lineno = -1

        elif event == 'line':
            try:
                # mask-out tracing
                self.enabled = False
                # record the line being executed
                self.pipeline.zincrby(filename, str(self.last_lineno) + ',' + str(lineno), 1)
            except Exception as e:
                log and log.warning('%s._trace got error: %r' % (self, e))
            finally:
                # un-mask tracing
                self.enabled = True
                self.last_lineno = lineno

        elif event == 'return':
            try:
                # mask-out tracing
                self.enabled = False
                # record return arc
                self.pipeline.zincrby(filename, str(self.last_lineno) + ',' + str(-frame.f_code.co_firstlineno), 1)
                # flush what we've got and start catching events into pipeline again
                # in case not all operations made it to the server, print a warning
                if not all(self.pipeline.execute()):
                    log and log.warning('%s._trace: pipeline.execute missed events' % self)
            except Exception as e:
                # self.__dell__ messes with tracing&logging
                log and log.warning('%s._trace got error: %r' % (self, e))
            finally:
                # un-mask tracing
                self.enabled = True
                self.last_lineno = self.stack.pop()

        elif event == 'exception':
            self.last_exc_back = frame.f_back

        # end processing
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

    def __del__(self):
        import sys
        sys.settrace(None)


