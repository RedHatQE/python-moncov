# test case tools for moncov tests
import logging
import re
import os
import contextlib
import moncov
import unittest
import imp
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
    extsplit = filename.split(os.path.extsep)
    if len(extsplit) > 1:
        # filename has extension
        if extsplit[-1].startswith('py'):
            extsplit[-1] = 'pyc?'
    filename = os.path.extsep.join(extsplit)
    return [re.compile(filename)]

def get_code_submodule_tuple(modulename):
    return imp.find_module(modulename, ['./test/code', './code', './'])

def code_submodule_whitelist(modulename):
    '''return code submodule whitelist'''
    _, filename, _ = get_code_submodule_tuple(modulename)
    return get_pyfilename_whitelist('.*' + filename)

@contextlib.contextmanager
def tracing_import_code_submodule(modulename, db=None):
    '''context for tracing import'''
    whitelist = code_submodule_whitelist(modulename)
    with tracing(db=db, whitelist=whitelist, blacklist=[]):
        try:
            yield imp.load_module(modulename, *get_code_submodule_tuple(modulename))
        finally:
            pass

class GenericMoncovTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        '''get reference to the db'''
        cls.db = moncov.conf.get_db(dbname="%s_db" % cls.__name__)

    @classmethod
    def tearDownClass(cls):
        '''close the db session'''
        moncov.ctl.disable()
        moncov.ctl.drop(db=cls.db)
        cls.db.connection.close()
        pass

    def setUp(self):
        '''prepare clean db'''
        moncov.ctl.drop(db=self.db)
        moncov.ctl.init(db=self.db)
        pass

    def tearDown(self):
        '''clean-up db'''
        moncov.ctl.drop(db=self.db)
        pass

    def assertResultBranchRate(self, rate):
        '''assert single result branch rate'''
        result = moncov.stats.simple.get_stats(db=self.db, whitelist=[re.compile('.*')], blacklist=[])
        assert len(result) == 1, "just a single file measured: %r" % result
        status = result[0]
        self.assertEqual(status.branch_rate, rate)

    def assertResultLineRate(self, rate):
        '''assert single result line rate'''
        result = moncov.stats.simple.get_stats(db=self.db, whitelist=[re.compile('.*')], blacklist=[])
        assert len(result) == 1, "just a single file measured: %r" % result
        status = result[0]
        self.assertEqual(status.line_rate, rate)
