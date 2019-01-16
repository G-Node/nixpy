import pytest
import tempfile
from nixio.test.xcompat.compile import maketests


BINDIR = tempfile.mkdtemp(prefix="nixpy-tests-")
xcavail = maketests(BINDIR)


def pytest_addoption(parser):
    parser.addoption("--force-compat", action="store_true", default=False,
                     help=("Force run compatibility tests. "
                           "If they fail to compile (e.g., missing NIX) "
                           "the tests wont pass.")
                     )


@pytest.fixture
def bindir(request):
    return BINDIR


def pytest_collection_modifyitems(config, items):
    if config.getoption("--force-compat"):
        print("Forcing compatibility tests")
        return
    if not xcavail:
        print("Skipping compatibility tests")
        skip_compat = pytest.mark.skip(
            reason="Compatibility tests require the NIX library"
        )
        for item in items:
            if "compatibility" in item.keywords:
                item.add_marker(skip_compat)
