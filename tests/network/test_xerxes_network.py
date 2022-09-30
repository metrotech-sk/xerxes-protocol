import warnings
import pytest
from xerxes_protocol.network import XerxesNetwork, FutureXerxesNetwork


@pytest.fixture
def com_is_not_opened(com_port):
    return com_port is None


def test_com_port():
    if com_is_not_opened:
        warnings.warn(UserWarning("Serial port is not opened. skipping bunch of tests!"))


@pytest.mark.skipif(com_is_not_opened, reason="Requires opened com port")
class TestNetwork:
    def test_1(self):
        assert True


class TestFutureNetwork:
    def test_send(self):
        with pytest.raises(NotImplementedError):
            fn = FutureXerxesNetwork()
            fn.send_msg(None, None)

    def test_read(self):
        with pytest.raises(NotImplementedError):
            fn = FutureXerxesNetwork()
            fn.read_msg()
