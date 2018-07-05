def pytest_addoption(parser):
    parser.addoption("--force-compat",
                     action="store_true",
                     default=False,
                     help=("Force cross-compatibility tests. "
                           "Raise error instead of skipping."))
