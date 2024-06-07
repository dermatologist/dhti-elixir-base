from kink import di

def get_di(mydi: str):
    _module = mydi.split("_", 1)[0]
    _mydi = mydi.split("_", 1)[1]
    try:
        return di[_module + "_" + _mydi]
    except KeyError:
        return di[_mydi]