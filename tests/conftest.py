from .bootstrap import bootstrap


def pytest_configure(config):
    print("Bootstrapping...")
    bootstrap()

