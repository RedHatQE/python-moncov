import moncov
import unittest
import inspect
import re
import contextlib
import logging
import pprint
from fractions import Fraction


log = logging.getLogger(__name__)


@contextlib.contextmanager
def tracing(db=None, whitelist=None, blacklist=None):
    '''context manager that enables moncov tracing'''
    collector = moncov.ctl.enable(db=db, whitelist=whitelist, blacklist=blacklist)
    try:
        yield collector
    finally:
        moncov.ctl.disable()
        log.debug('%r events: %r' % (db,
                    [event for event in db.events.find()]))
        moncov.stats.update.update(db=db)
        log.debug('%r lines: %r' % (db,
                    [line for line in db.lines.find()]))


def traced(db=None, whitelist=None, blacklist=None):
    '''a decorator enabling, disabling and updating moncov'''
    def tracer_wrapper(function):
        def tracer(*args, **kvs):
            with tracing(db, whitelist, blacklist):
                ret = function(*args, **kvs)
            return ret
        return tracer
    return tracer_wrapper


class MoncovTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        '''get reference to the db'''
        cls.db = moncov.conf.get_db(dbname="%s_db" % cls.__name__)
        cls.whitelist = []#[re.compile(re.escape(__file__))] # allow collecting this file only
        cls.blacklist = []#[re.compile('-------NOMATCH-------')] # FIXME blacklist [] results in a default
        pass

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

    def fileline(self):
        '''returns caller's current filename,lineno pair'''
        caller = inspect.currentframe().f_back
        return caller.f_code.co_filename, caller.f_lineno

    def test_01_notice(self):
        # enable tracing and count for this line
        @traced(self.db, self.whitelist, self.blacklist)
        def tmp():
            return self.fileline()
        filename, lineno = tmp()
        # assert the line was counted once
        response = self.db.lines.find_one({'_id.file': filename, '_id.line': lineno})
        assert response is not None
        self.assertGreater(response['value'], 0)

    def test_02_count(self):
        @traced(self.db, self.whitelist, self.blacklist)
        def tmp():
            return self.fileline()
        filename, lineno = tmp(); tmp()
        tmp(); tmp() ; tmp()
        response = self.db.lines.find_one({'_id.file': filename, '_id.line': lineno})
        assert response is not None
        self.assertEqual(response['value'], 5)

    def test_03_no_doublecount(self):
        @traced(self.db, self.whitelist, self.blacklist)
        def tmp():
            return self.fileline()
        filename, lineno = tmp()
        moncov.stats.update.update(self.db)
        response = self.db.lines.find_one({'_id.file': filename, '_id.line': lineno})
        assert response is not None
        self.assertEqual(response['value'], 1)

    def test_04_no_data_to_measure_stats(self):
        moncov.ctl.enable(db=self.db, whitelist=self.whitelist, blacklist=self.blacklist)
        moncov.ctl.disable()
        moncov.stats.update.update(self.db)
        result = moncov.stats.simple.get_stats(db = self.db)
        assert result == [], "nothing to measure"

    def test_05__50percent_branch_rate(self):
        @traced(self.db, self.whitelist, self.blacklist)
        def tmp(value):
            if value:
                pass
        tmp(True)
        result = moncov.stats.simple.get_stats(db = self.db)
        assert len(result) == 1, "just a single file measured"
        status = result[0]
        self.assertEqual(status.branch_rate, Fraction(1,2))


    def test_06__100percent_branch_rate(self):
        @traced(self.db, self.whitelist, self.blacklist)
        def tmp(value):
            if value:
                pass
        tmp(True); tmp(False)
        result = moncov.stats.simple.get_stats(db = self.db)
        assert len(result) == 1, "just a single file measured"
        status = result[0]
        self.assertEqual(status.branch_rate, Fraction(1,1))

    def test_07_100percent_branch_rate_ifelse(self):
        @traced(self.db, self.whitelist, self.blacklist)
        def tmp(value):
            if value:
                pass
            else:
                None # FIXME pass in here breaks the test case
        tmp(False); tmp(True);
        result = moncov.stats.simple.get_stats(db = self.db)
        assert len(result) == 1, "just a single file measured"
        status = result[0]
        self.assertEqual(status.branch_rate, Fraction(1,1))


    def _test_07__50percent_line_rate(self):
        def tmp(value):
            if value:
                pass
        moncov.ctl.enable(db=self.db)
        tmp(False)
        moncov.ctl.disable()
        moncov.stats.update.update(self.db)
        result = moncov.stats.simple.get_stats(db = self.db)
        assert len(result) == 1, "just a single file measured"
        status = result[0]
        self.assertEqual(status.line_rate, Fraction(1,2))


    def _test_08__100percent_line_rate(self):
        def tmp(value):
            if value:
                pass
        moncov.ctl.enable(db=self.db)
        tmp(True)
        moncov.ctl.disable()
        moncov.stats.update.update(self.db)
        result = moncov.stats.simple.get_stats(db = self.db)
        assert len(result) == 1, "just a single file measured"
        status = result[0]
        self.assertEqual(status.line_rate, Fraction(1,1))





