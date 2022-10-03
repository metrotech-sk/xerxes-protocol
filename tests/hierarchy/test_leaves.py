import warnings
import pytest
import serial
import pty
import os
from xerxes_protocol.hierarchy.leaves.utils import leaf_generator
from xerxes_protocol.network import Addr, XerxesNetwork
from xerxes_protocol.hierarchy.root import XerxesRoot
from xerxes_protocol.hierarchy.leaves.leaf import Leaf

class TestLeaf:
    def test_generated(self, com_port, hw_com):
        xn = XerxesNetwork(com_port).init()
        xr = XerxesRoot(xn, Addr(0))
        
        l = Leaf(Addr(1), xr)
        if hw_com:
            leaf = leaf_generator(l)
            assert l != leaf
        
        
class TestPressureLeaf: ...