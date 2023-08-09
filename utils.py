def class_method_wrapper(method, pre=None, post=None):
    def wrapped_method(self, *args):
        pre(self, None, *args) if pre else None
        rv = method(self, *args)
        post(self, rv, *args) if post else None
        return rv
    return wrapped_method

def print_expired_insects(self, rv, *args):
    if self.health <= args[0]:
        print('{0}({1}) ran out of health and expired'.format(
            type(self).__name__, self.place))

def print_thrower_target(self, rv, *args):
    if rv is not None:
        print('{0} targeted {1}'.format(self, rv))
