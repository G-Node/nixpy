import os

def is_running_under_pytest():
    return "PYTEST_CURRENT_TEST" in os.environ