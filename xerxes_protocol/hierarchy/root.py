#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import struct
import time
from typing import Union
from xerxes_protocol.defaults import (
    DEFAULT_BROADCAST_ADDRESS,
    PROTOCOL_VERSION_MAJOR,
    PROTOCOL_VERSION_MINOR
)
from xerxes_protocol.ids import MsgId, DevId
from xerxes_protocol.network import (
    Addr,
    XerxesNetwork,
    NetworkError,
    XerxesPingReply
)


__author__ = "theMladyPan"
__version__ = "1.4.0"
__license__ = "MIT"
__email__ = "stanislav@rubint.sk"
__status__ = "Production"
__package__ = "xerxes_protocol"
__date__ = "2023-02-22"

__all__ = [
    "XerxesRoot",
    "BROADCAST_ADDR"
]


BROADCAST_ADDR = Addr(DEFAULT_BROADCAST_ADDRESS)


class XerxesRoot:
    """Root node of the Xerxes network.

    This class is the root node of the Xerxes network. It is used to send and
    receive messages from the network. It is also used to send and receive
    messages from the leaves.

    Args:
        my_addr (Union[Addr, int, bytes]): The address of this node.
        network (XerxesNetwork): The network to use.

    Attributes:
        _addr (Addr): The address of this node.
        network (XerxesNetwork): The network to use.
    """
    def __init__(self, my_addr: Union[int, bytes], network: XerxesNetwork):
        if isinstance(my_addr, int) or isinstance(my_addr, bytes):
            self._addr = Addr(my_addr)
        elif isinstance(my_addr, Addr):
            self._addr = my_addr
        else:
            raise TypeError(f"my_addr type wrong, expected Union[Addr, int, bytes], got {type(my_addr)} instead")  # noqa: E501
        assert isinstance(network, XerxesNetwork)
        self.network = network


    def __repr__(self) -> str:
        return f"XerxesRoot(my_addr={self._addr}, network={self.network})"


    def send_msg(self, destination: Addr, payload: bytes) -> None:
        """Send a message to the network.

        Args:
            destination (Addr): The destination address.
            payload (bytes): The payload to send.
        """
        if not isinstance(payload, bytes):
            payload = bytes(payload)
        if not isinstance(destination, Addr):
            destination = Addr(destination)
        assert isinstance(payload, bytes)
        self.network.send_msg(
            source=self._addr,
            destination=destination,
            payload=payload
        )


    @property
    def address(self):
        return self._addr


    @address.setter
    def address(self, __v):
        self._addr = Addr(__v)


    def broadcast(self, payload: bytes) -> None:
        """Broadcast a message to the network = all nodes."""
        self.network.send_msg(
            source=self.address,
            destination=BROADCAST_ADDR,
            payload=payload
        )


    def sync(self) -> None:
        """Send a sync message to the network."""
        self.broadcast(payload=bytes(MsgId.SYNC))


    def ping(self, addr: Addr) -> XerxesPingReply:
        """Ping a node on the network.

        Args:
            addr (Addr): The address of the node to ping.
        
        Returns:
            XerxesPingReply: The ping reply. Contains the latency, the device
                ID, and the protocol version.
        """
        start = time.perf_counter()

        self.network.send_msg(
            source=self.address,
            destination=addr,
            payload=bytes(MsgId.PING)
        )
        reply = self.network.read_msg()
        end = time.perf_counter()
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


    @staticmethod
    def isPingLatest(pingPacket: XerxesPingReply) -> bool:
        """Check if the ping reply is the latest version of the protocol

        Args:
            pingPacket (XerxesPingReply): Ping packet to check

        Returns:
            bool: True if the ping reply is the latest version of the protocol
        """
        return (
            pingPacket.v_maj == PROTOCOL_VERSION_MAJOR and
            pingPacket.v_min == PROTOCOL_VERSION_MINOR
        )
