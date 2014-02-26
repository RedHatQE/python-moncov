
def disable():
    '''disable coverage collecting'''
    import sys
    sys.settrace(None)


def enable():
    '''enable coverage collecting'''
    import moncov
    c = moncov.Collector()
    c.start()
    
