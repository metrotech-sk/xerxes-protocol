#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from xerxes_protocol.hierarchy.leaves.leaf import Leaf
from xerxes_protocol.hierarchy.leaves.inclination import ILeaf
from xerxes_protocol.hierarchy.leaves.pressure import PLeaf
from xerxes_protocol.hierarchy.leaves.distance import DLeaf
from xerxes_protocol.hierarchy.leaves.strain import SLeaf
from xerxes_protocol.network import XerxesPingReply
from xerxes_protocol.ids import DevId


leaf_types = {
    DevId.ANGLE_XY_90: ILeaf,
    DevId.PRESSURE_600MBAR_2TEMP: PLeaf,
    DevId.PRESSURE_60MBAR_2TEMP: PLeaf,
    DevId.DIST_225MM: DLeaf,
    DevId.DIST_22MM: DLeaf,
    DevId.STRAIN_24BIT_2TEMP: SLeaf
}


class UnknownDevice(Exception): ...


def leaf_generator(leaf: Leaf) -> Leaf:
    ping_reply = leaf.ping()
    dev_id = ping_reply.dev_id
    if leaf_types.get(dev_id):
        return leaf_types.get(dev_id)(addr=leaf.address, root=leaf.root)
    else:
        raise UnknownDevice(f"Device id {dev_id} is not recognised.")