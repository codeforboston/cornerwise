import utils


class multimethod(object):
    def __init__(self, fn):
        self.default_fn = None
        self.dispatch_fn = fn
        self.table = {}

    def add(self, dispatch_val, fn=None):
        def adder(fn):
            self.table[dispatch_val] = fn

        if fn:
            adder(fn)
        else:
            return adder

    @property
    def default(self):
        def adder(fn):
            self.default_fn = fn
        return adder

    def __call__(self, *args):
        val = self.dispatch_fn(*args)

        if val in self.table:
            return self.table[val](*args)
        elif self.default_fn:
            return self.default_fn(*args)
        else:
            raise ValueError("Unknown dispatch value:", val)

def extension(path):
    return utils.extension(path).lower()


published_date = multimethod(extension)
published_date.default(lambda _: None)

encoding = multimethod(extension)
encoding.default(lambda _: "utf-8")
