#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass
import struct
from typing import List, Union

from xerxes_protocol.ids import DevId, MsgId
from xerxes_protocol.network import Addr, XerxesMessage, XerxesPingReply
from xerxes_protocol.hierarchy.root import XerxesRoot


@dataclass
class LeafData(object): ...
    # addr: int
    
    
def with_register(cls):
    for key in cls.register.keys():
        def __getter(cls):
            return cls.read_reg_by_key(key)
        
        def __setter(cls, __v):
            return cls.write_reg_by_key(key, __v)
        
        setattr(cls, key, property(fget=__getter, fset=__setter))     
    return cls
    

@with_register
class Leaf:
    register = {
        "address_offset": [0, "B"],
        "status": [0x80, "B"],
        "error": [0x81, "B"]
    }
    
    def __init__(self, addr: Addr, root: XerxesRoot):
        assert(isinstance(addr, Addr))
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
        return self.exchange(MsgId.FETCH_MEASUREMENT.bytes)
    
    
    def read_reg(self, reg_addr: int, length: int) -> bytes:
        length = int(length)
        reg_addr = int(reg_addr)
        payload = bytes(MsgId.READ_REQ) + reg_addr.to_bytes(1, "little") + length.to_bytes(1, "little")
        return self.exchange(payload)
    
    
    def write_reg(self, reg_addr: int, value: bytes) -> bytes:
        reg_addr = int(reg_addr)
        payload = bytes(MsgId.WRITE) + reg_addr.to_bytes(1, "little") + value
        return self.exchange(payload)
    

    def read_reg_by_key(self, key: str) -> Union[int, float]:
        assert self.register.get(key), f"Key {key} is not in register."
        val_type = self.register.get(key)[1]
        rm: XerxesMessage
        if val_type == "B":
            rm = self.read_reg(self.register.get(key)[0], 1)
        else:
            rm = self.read_reg(self.register.get(key)[0], 4)
        
        val = rm.payload
        return struct.unpack(val_type, val)[0]
    
    
    def write_reg_by_key(self, key: str, value: Union[int, float]) -> None:
        assert self.register.get(key), f"Key {key} is not in register."
        
        payload = struct.pack(self.register.get(key)[1], value)
        self.write_reg(self.register.get(key)[0], payload)


    @property
    def address(self):
        return self._address


    @address.setter
    def address(self, __v):
        raise NotImplementedError("Address should not be changed")


    def __repr__(self) -> str:
        return f"Leaf(address={self.address}, root={self.root})"


    def __str__(self) -> str:
        return self.__repr__()

