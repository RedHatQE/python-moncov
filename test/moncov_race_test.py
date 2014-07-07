import unittest
import multiprocessing
import moncov

__test__ = False # FIXME

def traced_fileline(dbdetails, **kvs): 
    '''returns current filename,lineno pair and ensures the line being traced by moncov'''
    import inspect
    import moncov
    def tmp():
        frame = inspect.currentframe()
        return frame.f_code.co_filename, frame.f_lineno
    dbhost, dbport, dbname = dbdetails
    moncov.ctl.enable(dbhost=dbhost, dbport=dbport, dbname=dbname)
    filename, lineno = tmp()
    moncov.ctl.disable()
    return filename, lineno


def subprocess_dbupdate(dbdetails, **kvs):
    '''call moncov stats update from a subprocess'''
    import moncov
    dbhost, dbport, dbname = dbdetails
    moncov.stats.update.update(dbhost=dbhost, dbport=dbport, dbname=dbname)


class MoncovRaceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        '''get reference to the db'''
        cls.db = moncov.conf.get_db(dbname="%s_db" % cls.__name__)
        cls.db_details = moncov.conf.get_dbdetails(cls.db)

    @classmethod
    def tearDownClass(cls):
        '''close the db session'''
        moncov.ctl.disable()
        moncov.ctl.drop(db=cls.db)
        cls.db.connection.close()

    def setUp(self):
        '''prepare clean db'''
        moncov.ctl.drop(db=self.db)
        moncov.ctl.init(db=self.db)

    def tearDown(self):
        '''clean-up db'''
        moncov.ctl.drop(db=self.db)

    def test_01_count(self):
        poolsize = 64
        pool = multiprocessing.Pool(poolsize)
        result = pool.map(traced_fileline, [self.db_details] * poolsize)
        moncov.stats.update.update(self.db)
        # result should contain same filename,lineno pairs
        assert len(set(result)) == 1, "all result records are the same"
        filename, lineno = result[0]
        # assert the filename, lineno was encounted
        response = self.db.lines.find_one({'_id.file': filename, '_id.line': lineno})
        assert response is not None
        # assert the filename, lineno was hit at most as many times as there were processes
        self.assertLessEqual(response['value'], poolsize)
        # assert there are precisely poolsize number of events
        self.assertEqual(len(list(self.db.events.find({'file': filename, 'line': lineno}))), poolsize)

    def test_02_no_doublecount(self):
        # call a subprocess tracing a line
        pool = multiprocessing.Pool(1)
        filename, lineno = pool.map(traced_fileline, [self.db_details])[0]
        # assert the line event was reported just once
        self.assertEqual(len(list(self.db.events.find({'file': filename, 'line': lineno}))), 1)
        # call concurrent update
        poolsize = 64
        pool = multiprocessing.Pool(poolsize)
        pool.map(subprocess_dbupdate, [self.db_details] * poolsize)
        # assert the filename, lineno was encounted
        response = self.db.lines.find_one({'_id.file': filename, '_id.line': lineno})
        assert response is not None
        # assert the hit count is 1 i.e. the concurrent update didn't break the counting 
        self.assertLessEqual(response['value'], 1)
