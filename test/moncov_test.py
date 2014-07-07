import moncov
import unittest
import inspect
import logging
from tools import get_pyfilename_whitelist, traced


log = logging.getLogger(__name__)



class MoncovTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        '''get reference to the db'''
        cls.db = moncov.conf.get_db()
        cls.whitelist = get_pyfilename_whitelist(__file__)
        cls.blacklist = []

    @classmethod
    def tearDownClass(cls):
        '''close the db session'''
        moncov.ctl.disable()
        moncov.ctl.drop(db=cls.db)

    def setUp(self):
        '''prepare clean db'''
        moncov.ctl.drop(db=self.db)

    def tearDown(self):
        '''clean-up db'''
        moncov.ctl.drop(db=self.db)

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

    def test_sanity(self):
        # enable tracing and count for this line
        @traced(self.db, self.whitelist, self.blacklist)
        def tmp():
            return self.fileline()
        filename, lineno = tmp()
        # assert the file was collected
        self.assertTrue(self.db.sismember('filenames', filename))
        # assert there are collected records
        self.assertNotEqual([], moncov.data.filename_arcs(self.db, filename))

        # sanity
        self.assertIn(filename, moncov.data.filenames(self.db))
        arcs = moncov.data.filename_arcs(self.db, filename)
        # lineno met
        arc_matches = [lineno == moncov.data.arc2line(arc) for arc in arcs]
        self.assertTrue(any(arc_matches))
        # hits count match
        index = arc_matches.index(True)
        self.assertEqual(1, moncov.data.filename_arc_hits(self.db, filename, arcs[index]))


