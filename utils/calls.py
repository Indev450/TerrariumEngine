import weakref


class Call:

    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        return self.func(*self.args, **self.kwargs)


class WeakCall:
    
    def __init__(self, func, *args, **kwargs):
        if not hasattr(func, '__func__'):
            raise ValueError('only methods can be passed in WeakCall. Use Call instead')
        
        self.func = WeakMethod(func)
        
        self.args = args
        self.kwargs = kwargs
        
    def __call__(self):
        return self.func(*self.args, **self.kwargs)


class WeakMethod:
    
    def __init__(self, call):
        self.func = call.__func__
        
        self.obj = weakref.ref(call.__self__)
    
    def __call__(self, *args, **kwargs):
        obj = self.obj()
        
        if obj is not None:
            return self.func(*((obj, ) + args), **kwargs)


class CallOnce:

    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.called = False

    def __call__(self):
        if not self.called:
            return self.func(*self.args, **self.kwargs)

    def copy(self):
        return CallOnce(self.func, *self.args, **self.kwargs)
