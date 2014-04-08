# test case tools for moncov tests
import logging
import re
import os
import contextlib
import moncov
log = logging.getLogger(__name__)

@contextlib.contextmanager
def tracing(db=None, whitelist=None, blacklist=None):
    '''context manager that enables moncov tracing'''
    collector = moncov.ctl.enable(db=db, whitelist=whitelist, blacklist=blacklist)
    try:
        yield collector
    finally:
        moncov.ctl.disable()
        log.debug('%r events:' % db)
        for event in db.events.find():
            log.debug('  %r' % event)
        moncov.stats.update.update(db=db)
        log.debug('%r lines:' % db)
        for line in db.lines.find():
            log.debug('  %r' % line)


def traced(db=None, whitelist=None, blacklist=None):
    '''a decorator enabling, disabling and updating moncov'''
    def tracer_wrapper(function):
        def tracer(*args, **kvs):
            with tracing(db, whitelist, blacklist):
                ret = function(*args, **kvs)
            return ret
        return tracer
    return tracer_wrapper

def get_pyfilename_whitelist(filename):
    '''return a re.compiled pattern that matches any *.py(c)? of the filename present'''
    escaped = re.escape(filename)
    extsplit = escaped.split(os.path.extsep)
    if len(extsplit) > 1:
        # filename has extension
        if extsplit[-1].startswith('py'):
            extsplit[-1] = 'pyc?'
    escaped = os.path.extsep.join(extsplit)
    return [re.compile(escaped)]


