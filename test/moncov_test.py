import moncov
import unittest
import inspect
import re
import contextlib
import logging
import pprint
from fractions import Fraction
from tools import (traced, get_pyfilename_whitelist)


log = logging.getLogger(__name__)



class MoncovTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        '''get reference to the db'''
        cls.db = moncov.conf.get_db(dbname="%s_db" % cls.__name__)
        cls.whitelist = get_pyfilename_whitelist(__file__) # allow collecting this file only
        cls.blacklist = []
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

    def assertResultBranchRate(self, rate):
        '''assert single result branch rate'''
        result = moncov.stats.simple.get_stats(db = self.db)
        assert len(result) == 1, "just a single file measured: %r" % result
        status = result[0]
        self.assertEqual(status.branch_rate, rate)

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
        self.assertResultBranchRate(Fraction(1,2))


    def test_06__100percent_branch_rate(self):
        @traced(self.db, self.whitelist, self.blacklist)
        def tmp(value):
            if value:
                pass
        tmp(True); tmp(False)
        self.assertResultBranchRate(Fraction(1,1))

    def test_07_100percent_branch_rate_ifelse(self):
        @traced(self.db, self.whitelist, self.blacklist)
        def tmp(value):
            if value:
                pass
            else:
                None # FIXME pass in here breaks the test case
        tmp(False); tmp(True);
        self.assertResultBranchRate(Fraction(1,1))

    def test_08_50percent_branch_rate_multiline_test(self):
        @traced(self.db, self.whitelist, self.blacklist)
        def tmp(value):
            if False or \
                    value:
                pass
        tmp(True)
        self.assertResultBranchRate(Fraction(1,2))

    def _test_09_100percent_branch_rate_multiline_test(self):
        @traced(self.db, self.whitelist, self.blacklist)
        def tmp(value):
            if False or \
                    value:
                pass
            else:
                None
        tmp(True); tmp(False)
        result = moncov.stats.simple.get_stats(db = self.db)
        assert len(result) == 1, "just a single file measured"
        status = result[0]
        self.assertEqual(status.branch_rate, Fraction(2,2))

    def test_10_50percent_branch_rate_For_multiline_empty(self):
        @traced(self.db, self.whitelist, self.blacklist)
        def tmp(iterable):
            for x in \
                    iterable:
                pass
        tmp([])
        self.assertResultBranchRate(Fraction(1,2))

    def test_11_50percent_branch_rate_For_multiline_nonempty(self):
        @traced(self.db, self.whitelist, self.blacklist)
        def tmp(iterable):
            for x in \
                    iterable:
                pass
        tmp([1,2])
        self.assertResultBranchRate(Fraction(1,2))

    def test_12_100percent_branch_rate_For_multiline(self):
        @traced(self.db, self.whitelist, self.blacklist)
        def tmp(iterable):
            for x in \
                    iterable:
                pass
        tmp([]); tmp([1,2])
        self.assertResultBranchRate(Fraction(2,2))

    def test_13_50percent_branch_rate_While_false(self):
        @traced(self.db, self.whitelist, self.blacklist)
        def tmp(value):
            i = 0
            while i < value:
                i += 1
        tmp(0)
        self.assertResultBranchRate(Fraction(1,2))

    def test_14_50percent_branch_rate_While_true(self):
        @traced(self.db, self.whitelist, self.blacklist)
        def tmp(value):
            i = 0
            while i < value:
                i += 1
        tmp(3)
        self.assertResultBranchRate(Fraction(1,2))

    def test_15_100percent_branch_rate_While(self):
        @traced(self.db, self.whitelist, self.blacklist)
        def tmp(value):
            i = 0
            while i < value:
                i += 1
        tmp(0); tmp(3)
        self.assertResultBranchRate(Fraction(2,2))
