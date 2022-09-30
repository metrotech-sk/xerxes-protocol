import pytest
from xerxes_protocol.network import XerxesNetwork
import warnings


@pytest.fixture
def com_is_not_opened(com_port):
    return com_port == None


def test_com_port(com_port):
    warnings.warn(UserWarning(f"Serial port is not opened. skipping bunch of tests!"))


@pytest.mark.skipif(com_is_not_opened, reason="Requires opened com port")
class TestNetwork:
    def test_1():
        assert True