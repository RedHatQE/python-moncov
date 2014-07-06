'''data manipulation stuff'''

def arc2tuple(arc):
    '''convert moncov arc "1,2" to a lineno tuple (1, 2)'''
    first, last = arc.split(',')
    return int(first), int(last)

def arc2line(arc):
    '''convert moncov arc "1,2" to an executed lineno 2'''
    first, last = arc.split(',')
    last = int(last)
    if last < 0:
        last = - last
    return last

def filenames(db):
    '''return collected/measured filenames'''
    return db.smembers('filenames')

def filename_arcs(db, filename):
    '''return collected filename arcs'''
    return db.zrange(filename, 0, -1)

def filename_arc_hits(db, filename, arc):
    '''return hit count of a filename arc'''
    return db.zrank(filename, arc)
