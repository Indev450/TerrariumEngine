def hasattrs(obj, attrs, listmissing=False):
    if not attrs:
        return True, [] if listmissing else ''
    
    missing = []
    
    for attr in attrs:
        if not hasattr(obj, attr):
            if not listmissing:
                return False, attr
            else:
                missing.append(attr)
    
    if listmissing:
        return len(missing) == 0, missing
    
    return True, ''
