def wrapped(f):
    def replace(*args, **kwargs):
        return f(*args, **kwargs)
    return replace
