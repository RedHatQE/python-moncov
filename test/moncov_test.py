import moncov
import unittest
import inspect
from fractions import Fraction



class MoncovTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        '''get reference to the db'''
        cls.db = moncov.conf.get_db(dbname="%s_db" % cls.__name__)
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
        moncov.ctl.enable(db=self.db)
        def tmp():
            return self.fileline()
        filename, lineno = tmp()
        moncov.ctl.disable()
        moncov.stats.update.update(self.db)
        # assert the line was counted once
        response = self.db.lines.find_one({'_id.file': filename, '_id.line': lineno})
        assert response is not None
        self.assertGreater(response['value'], 0)

    def test_02_count(self):
        def tmp():
            return self.fileline()
        moncov.ctl.enable(db=self.db)
        filename, lineno = tmp(); tmp()
        tmp(); tmp() ; tmp()
        moncov.ctl.disable()
        moncov.stats.update.update(self.db)
        response = self.db.lines.find_one({'_id.file': filename, '_id.line': lineno})
        assert response is not None
        self.assertEqual(response['value'], 5)

    def test_03_no_doublecount(self):
        def tmp():
            return self.fileline()
        moncov.ctl.enable(db=self.db)
        filename, lineno = tmp()
        moncov.ctl.disable()
        moncov.stats.update.update(self.db)
        moncov.stats.update.update(self.db)
        response = self.db.lines.find_one({'_id.file': filename, '_id.line': lineno})
        assert response is not None
        self.assertEqual(response['value'], 1)

    def test_04_no_data_to_measure_stats(self):
        def tmp(value):
            if value:
                pass
        moncov.ctl.enable(db=self.db)
        moncov.ctl.disable()
        moncov.stats.update.update(self.db)
        result = moncov.stats.simple.get_stats(db = self.db)
        assert result == [], "nothing to measure"
        
    def test_05__50percent_branch_rate(self):
        def tmp(value):
            if value:
                pass
        moncov.ctl.enable(db=self.db)
        tmp(True); 
        moncov.ctl.disable()
        moncov.stats.update.update(self.db)
        result = moncov.stats.simple.get_stats(db = self.db)
        assert len(result) == 1, "just a single file measured"
        status = result[0]
        self.assertEqual(status.branch_rate, Fraction(1,2))

        
    def test_06__100percent_branch_rate(self):
        def tmp(value):
            if value:
                pass
        moncov.ctl.enable(db=self.db)
        tmp(True); tmp(False)
        moncov.ctl.disable()
        moncov.stats.update.update(self.db)
        result = moncov.stats.simple.get_stats(db = self.db)
        assert len(result) == 1, "just a single file measured"
        status = result[0]
        self.assertEqual(status.branch_rate, Fraction(1,1))

        



