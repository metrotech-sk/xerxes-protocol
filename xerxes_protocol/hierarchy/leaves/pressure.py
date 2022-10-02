#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from xerxes_protocol.ids import MsgId
from xerxes_protocol.hierarchy.leaves.leaf import Leaf, LeafData, with_register
from xerxes_protocol.units.pressure import Pressure
from xerxes_protocol.units.temp import Celsius
import struct


@dataclass
class PLeafData(LeafData):
    pressure: Pressure
    temperature_sensor: Celsius
    temperature_external_1: Celsius
    temperature_external_2: Celsius


@with_register
class PLeaf(Leaf):
    register = Leaf.register
    register["offset"] = [0x10, "f"]
    register["gain"] = [0x14, "f"]
    register["t_k"] = [0x18, "f"]
    register["t_o"] = [0x1C, "f"]
    
    
    def fetch(self) -> PLeafData:
        reply = self.exchange(bytes(MsgId.FETCH_MEASUREMENT))

        values = struct.unpack("ffff", reply.payload)  # unpack 5 floats: pressure in Pa, temp_sensor, temp_e1, temp_e2

        # convert to sensible units
        return PLeafData(
            pressure=Pressure(values[0]),
            temperature_sensor=Celsius(values[1]),
            temperature_external_1=Celsius(values[2]),
            temperature_external_2=Celsius(values[3])
        )
        
            
    def __repr__(self):
        return f"PLeaf(addr={self.address}, root={self.root})"
    
    
    @property
    def offset(self):
        return self.read_reg_by_key("offset")
        
    
    @offset.setter
    def offset(self, _v):
        self.write_reg_by_key("offset", "f", _v)
        
    
    
        
        
    
        
    