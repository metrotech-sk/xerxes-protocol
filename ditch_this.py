#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from xerxes_protocol.network import XerxesNetwork, Addr
from xerxes_protocol.hierarchy.root import XerxesRoot
from xerxes_protocol.hierarchy.leaves.leaf import Leaf
from xerxes_protocol.hierarchy.leaves.utils import leaf_generator

import serial, os

xn = XerxesNetwork(serial.Serial("/dev/ttyUSB0", baudrate=115200, timeout=0.02)).init()
xr = XerxesRoot(Addr(0), xn)
xl = Leaf(Addr(1), xr)
xpl = leaf_generator(xl)
xpl.write_param("t_k", 0)
xpl.reset_soft()
print(xpl.read_param("t_k"))
xr.sync()
print(xpl.fetch())