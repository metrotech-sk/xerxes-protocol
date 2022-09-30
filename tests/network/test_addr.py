from xerxes_protocol.network import Addr
import pytest


class TestAddr:
    def test_type_1(self):
        a = Addr(1)
        assert int(a) == 1
        assert bytes(a) == b"\x01"
        
    def test_length_1(self):
        with pytest.raises(AssertionError):
            a1 = Addr(-1)
            
            
    def test_length_2(self):
        with pytest.raises(AssertionError):
            a1 = Addr(256)
            
    
    def test_eq_1(self):
        Addr(0x01) == Addr(b"\x01")
        
    