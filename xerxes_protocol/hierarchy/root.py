#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import struct
import time
from typing import Union

from xerxes_protocol.defaults import DEFAULT_BROADCAST_ADDRESS
from xerxes_protocol.ids import MsgId, DevId
from xerxes_protocol.network import Addr, XerxesNetwork, NetworkError, XerxesPingReply

BROADCAST_ADDR = Addr(DEFAULT_BROADCAST_ADDRESS)

class XerxesRoot:
    def __init__(self, my_addr: Union[int, bytes], network: XerxesNetwork):        
        if isinstance(my_addr, int) or isinstance(my_addr, bytes):
            self._addr = Addr(my_addr)
        elif isinstance(my_addr, Addr):
            self._addr = my_addr
        else:
            raise TypeError(f"my_addr type wrong, expected Union[Addr, int, bytes], got {type(my_addr)} instead")
        assert isinstance(network, XerxesNetwork)
        self.network = network


    def __repr__(self) -> str:
        return f"XerxesRoot(my_addr={self._addr}, network={self.network})"


    def send_msg(self, destination: Addr, payload: bytes) -> None:
        if not isinstance(destination, Addr):
            destination = Addr(destination)
        assert isinstance(payload, bytes)
        self.network.send_msg(source=self._addr, destination=destination, payload=payload)
    
    
    @property
    def address(self):
        return self._addr


    @address.setter
    def address(self, __v):
        self._addr = Addr(__v)
    

    def broadcast(self, payload: bytes) -> None:
        self.network.send_msg(source=self.address, destination=BROADCAST_ADDR, payload=payload)
        

    def sync(self) -> None:
        self.broadcast(payload=bytes(MsgId.SYNC))
        
        
    def ping(self, addr: Addr):
        start = time.monotonic()

        self.network.send_msg(
            source=self.address,
            destination=addr,
            payload=bytes(MsgId.PING)
        )
        reply = self.network.read_msg()
        end = time.monotonic()
        if reply.message_id == MsgId.PING_REPLY:
            rpl = struct.unpack("BBB", reply.payload)
            return XerxesPingReply(
                dev_id=DevId(rpl[0]),
                v_maj=int(rpl[1]),
                v_min=int(rpl[2]),
                latency=(end - start)
            )
        else:
            NetworkError("Invalid reply received ({reply.message_id})")
