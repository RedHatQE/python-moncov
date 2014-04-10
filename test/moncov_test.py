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
        cls.db = moncov.conf.get_db(dbname="%s_db" % cls.__name__)
        cls.whitelist = get_pyfilename_whitelist(__file__)
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

