#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from xerxes_protocol.hierarchy.leaves.leaf import Leaf
from xerxes_protocol.hierarchy.leaves.inclination import ILeaf
from xerxes_protocol.hierarchy.leaves.pressure import PLeaf
from xerxes_protocol.ids import DevId


leaf_types = {
    DevId.ANGLE_XY_90: ILeaf,
    DevId.PRESSURE_600MBAR_2TEMP: PLeaf,
    DevId.PRESSURE_60MBAR_2TEMP: PLeaf,
}


def leaf_generator(leaf: Leaf) -> Leaf:
    prply = leaf.ping()
    dev_id = prply.dev_id
    return leaf_types.get(dev_id)(addr=leaf.address, root=leaf.root)