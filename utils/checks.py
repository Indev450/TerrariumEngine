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


def hasitems(collection, items, listmissing=False):
    if not items:
        return True, [] if listmissing else None
    
    missing = []
    
    for item in items:
        if item not in collection:
            if not listmissing:
                return False, item
            else:
                missing.append(item)
    
    if listmissing:
        return len(missing) == 0, missing
    
    return True, None
