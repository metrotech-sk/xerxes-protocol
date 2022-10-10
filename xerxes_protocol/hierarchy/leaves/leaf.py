#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass
import struct
from typing import List, Union
from rich import print
import time

from xerxes_protocol.ids import DevId, MsgId
from xerxes_protocol.network import Addr, InvalidMessage, XerxesMessage, XerxesPingReply
from xerxes_protocol.hierarchy.root import XerxesRoot
from xerxes_protocol.units.unit import Unit


@dataclass
class LeafData(object):
    # addr: int
    def _as_dict(self):
        d = {}
        for attribute in self.__dir__():
            if not attribute.startswith("_"):
                attr_val = self.__getattribute__(attribute)
                if isinstance(attr_val, (int, float, str, dict, list)):
                    d.update({
                        attribute: attr_val
                    })
                elif isinstance(attr_val, Unit):
                    d.update({
                        attribute: attr_val.preferred()
                    })
                    
        return d


class Leaf:
    parameters = {
        "address_offset": [0, "B"],
        "status": [0x80, "B"],
        "error": [0x81, "B"]
    }
    
    def __init__(self, addr: Addr, root: XerxesRoot):
        assert(isinstance(addr, Addr))
        assert isinstance(root, XerxesRoot)
        self._address = addr

        self.root: XerxesRoot
        self.root = root


    def ping(self) -> XerxesPingReply:
        return self.root.ping(bytes(self.address))


    def exchange(self, payload: bytes) -> XerxesMessage:
        # test if payload is list of uchars
        assert isinstance(payload, bytes)
        self.root.send_msg(self._address, payload)
        return self.root.network.read_msg()
        
    
    def fetch(self) -> XerxesMessage:
        return self.exchange(bytes(MsgId.FETCH_MEASUREMENT))
    
    
    def read_reg(self, reg_addr: int, length: int) -> bytes:
        length = int(length)
        reg_addr = int(reg_addr)
        payload = bytes(MsgId.READ_REQ) + reg_addr.to_bytes(1, "little") + length.to_bytes(1, "little")
        return self.exchange(payload)
    
    
    def write_reg(self, reg_addr: int, value: bytes) -> bytes:
        reg_addr = int(reg_addr)
        payload = bytes(MsgId.WRITE) + reg_addr.to_bytes(1, "little") + value
        
        self.root.send_msg(self._address, payload)
        reply = self.root.network.wait_for_reply(0.01*len(payload))  # it takes ~10ms for byte to be written to memory
        if reply.message_id == MsgId.ACK_OK:
            return reply
        else:
            raise RuntimeError("Register write unsuccessful.")
    

    def read_param(self, key: str) -> Union[int, float]:
        assert self.parameters.get(key), f"Key {key} is not in parameters."
        val_type = self.parameters.get(key)[1]
        rm: XerxesMessage
        if val_type == "B":
            rm = self.read_reg(self.parameters.get(key)[0], 1)
        else:
            rm = self.read_reg(self.parameters.get(key)[0], 4)
        
        val = rm.payload
        return struct.unpack(val_type, val)[0]
    
    
    def write_param(self, key: str, value: Union[int, float]) -> None:
        assert self.parameters.get(key), f"Key {key} is not in parameters."
        payload = struct.pack(self.parameters.get(key)[1], value)
        self.write_reg(self.parameters.get(key)[0], payload)


    def reset_soft(self):
        self.exchange(bytes(MsgId.RESET))


    @property
    def address(self):
        return self._address


    @address.setter
    def address(self, __v):
        raise NotImplementedError("Address should not be changed")


    def __repr__(self) -> str:
        return f"Leaf(addr={self.address}, root={self.root})"


    def __str__(self) -> str:
        return self.__repr__()


    @staticmethod
    def average(array: List[LeafData]) -> LeafData:
        assert isinstance(array, list)        
        assert isinstance(array[0], LeafData)
        
        average = {}
        for data in array:
            for attribute in data.__dir__():
                if not attribute.startswith("_"):
                    # if entry is not in the dict, create empty list
                    if not average.get(attribute):
                        average[attribute] = []
                        
                    # convert attribute val to reasonable number if necessary
                    attr_val = data.__getattribute__(attribute)
                    if isinstance(attr_val, Unit):
                        attr_val = attr_val.preferred()
                    average[attribute].append(attr_val)
                    
        average_class = LeafData()
        for key in average:
            averages = average[key]
            if len(averages) > 0:
                average_class.__setattr__(key, sum(averages)/len(averages))
        return average_class


    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, Leaf) and self._address == __o.address

    
    def __hash__(self) -> int:
        return hash(self.address)