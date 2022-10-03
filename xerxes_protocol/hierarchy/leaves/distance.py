#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from xerxes_protocol.ids import MsgId
from xerxes_protocol.hierarchy.leaves.leaf import Leaf, LeafData
from xerxes_protocol.units.length import Length
from xerxes_protocol.units.temp import Celsius
import struct


@dataclass
class DLeafData(LeafData):
    distance_1: Length
    distance_2: Length
    temperature_external_1: Celsius
    temperature_external_2: Celsius


class DLeaf(Leaf):
    parameters = Leaf.parameters.copy()
    parameters["offset"] = [0x10, "f"]
    parameters["gain"] = [0x14, "f"]
    parameters["t_k"] = [0x18, "f"]
    parameters["t_o"] = [0x1C, "f"]
    
    
    def fetch(self) -> DLeafData:
        reply = self.exchange(bytes(MsgId.FETCH_MEASUREMENT))

        values = struct.unpack("ffff", reply.payload)  # unpack 5 floats: pressure in Pa, temp_sensor, temp_e1, temp_e2

        # convert to sensible units
        return DLeafData(
            distance_1=Length(values[0]),
            distance_2=Length(values[1]),
            temperature_external_1=Celsius(values[2]),
            temperature_external_2=Celsius(values[3])
        )
        
            
    def __repr__(self):
        return f"DLeaf(addr={self.address}, root={self.root})"
    
        
    
        
    