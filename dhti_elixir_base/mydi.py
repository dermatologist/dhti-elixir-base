from kink import di

def get_di(mydi: str, default=None):
    _module = mydi.split("_", 1)[0]
    _mydi = mydi.split("_", 1)[1]
    try:
        return di[_module + "_" + _mydi]
    except KeyError:
        try:
            return di[_mydi]
        except KeyError:
            return default