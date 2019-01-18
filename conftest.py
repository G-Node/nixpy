import pytest
import tempfile
from nixio.test.xcompat.compile import maketests


BINDIR = tempfile.mkdtemp(prefix="nixpy-tests-")


def pytest_addoption(parser):
    parser.addoption("--nix-compat", action="store_true", default=False,
                     help=("Run nix compatibility tests "
                           "(requires NIX library)"))


@pytest.fixture
def bindir(request):
    return BINDIR


def pytest_collection_modifyitems(config, items):
    if config.getoption("--nix-compat"):
        print("Compiling NIX compatibility tests")
        maketests(BINDIR)
        return
    skip_compat = pytest.mark.skip(
        reason="Use --nix-compat option to run compatibility tests"
    )
    for item in items:
        if "compatibility" in item.keywords:
            item.add_marker(skip_compat)
