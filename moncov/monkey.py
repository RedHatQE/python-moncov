'''monkey patch hacks'''
import conf
import os

def _iter_filename_over_mountpoints(self, filename):
    '''iterate absolute filename over self.mountpoints and self.root'''
    for mountpoint in self.mountpoints + [self.root]:
        _drivename, _filename = os.path.splitdrive(filename)
        _filename = _filename.lstrip(os.path.sep)
        yield os.path.join(_drivename + mountpoint, _filename)

def patch_coveragepy(dbhost=conf.DBHOST, dbport=conf.DBPORT, dbname=conf.DBNAME, root=os.path.sep, mountpoints=[]):
    '''monkey patch coveragepy in order to fetch stats from our data store'''
    from coverage.data import CoverageData
    CoverageData.root = root
    CoverageData.mountpoints = mountpoints
    CoverageData.iter_filename_over_mountpoints = _iter_filename_over_mountpoints


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
            data['arcs'][filename] = list()
            data['lines'][filename] = list()
            for arc in moncov.data.filename_arcs(db, filename):
                data['arcs'][filename].append(moncov.data.arc2tuple(arc))
                data['lines'][filename].append(moncov.data.arc2line(arc))
            # duplicate with various mountpoints
            try:
                for mount_filename in self.iter_filename_over_mountpoints(filename):
                    data['arcs'][mount_filename] = data['arcs'][filename]
                    data['lines'][mount_filename] = data['lines'][filename]
            except Exception as e:
                import sys
                print sys.exc_info()
        self._moncov_data_cache = data
        return self._moncov_data_cache

    CoverageData.raw_data = raw_data

