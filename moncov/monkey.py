'''monkey patch hacks'''
import conf

def patch_coveragepy(dbhost=conf.DBHOST, dbport=conf.DBPORT, dbname=conf.DBNAME):
    '''monkey patch coveragepy in order to fetch stats from our data store'''
    import coverage

    def raw_data(self, arg_ignored):
        '''moncov patched raw data method to fetch stats from moncov data store'''
        import moncov
        db = moncov.conf.get_db(dbhost=dbhost, dbport=dbport, dbname=dbname)
        if hasattr(self, '_moncov_data_cache'):
            return self._moncov_data_cache

        data = {
            'arcs': {},
            'lines': {}
        }
        for filename in moncov.data.filenames(db):
            data['arcs'][filename] = []
            data['lines'][filename] = []
            for arc in moncov.data.filename_arcs(db, filename):
                data['arcs'][filename].append(moncov.data.arc2tuple(arc))
                data['lines'][filename].append(moncov.data.arc2line(arc))
        self._moncov_data_cache = data
        return self._moncov_data_cache

    coverage.data.CoverageData.raw_data = raw_data

