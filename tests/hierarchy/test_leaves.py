import warnings
import pytest
import serial
import pty
import os
from xerxes_protocol.network import Addr, XerxesNetwork
from xerxes_protocol.hierarchy.root import XerxesRoot
from xerxes_protocol.hierarchy.leaves.leaf import Leaf

class TestLeaf:
    def test_generated(self):
        master, slave = pty.openpty()
        s_name = os.ttyname(slave)
        
        xn = XerxesNetwork(serial.Serial(s_name)).init()
        xr = XerxesRoot(xn, Addr(0))
        
        l = Leaf(Addr(1), xr)
        properties = dir(l)
        assert "status" in properties and "error" in properties
        
        
class TestPressureLeaf: ...