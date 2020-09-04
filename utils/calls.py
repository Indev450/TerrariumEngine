class Call:

    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        return self.func(*self.args, **self.kwargs)


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
