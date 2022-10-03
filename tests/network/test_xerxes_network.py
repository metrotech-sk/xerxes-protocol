import warnings
import pytest
import serial
from xerxes_protocol.network import Addr, XerxesNetwork, FutureXerxesNetwork
from xerxes_protocol.ids import MsgId


class TestNetwork:
    def test_1(self, com_port):
        xn = XerxesNetwork(com_port)
        xn.init()
        assert xn.opened


    def test_ping(self, com_port, hw_com):
        xn = XerxesNetwork(com_port).init()
        xn.send_msg(Addr(0), Addr(1), bytes(MsgId.PING))
        try:
            rpl = xn.read_msg()
            assert rpl.message_id == MsgId.PING_REPLY
        except TimeoutError:
            if not hw_com: 
                pass
            else:
                raise


class TestFutureNetwork:
    def test_send(self):
        with pytest.raises(NotImplementedError):
            fn = FutureXerxesNetwork()
            fn.send_msg(None, None)

    def test_read(self):
        with pytest.raises(NotImplementedError):
            fn = FutureXerxesNetwork()
            fn.read_msg()
