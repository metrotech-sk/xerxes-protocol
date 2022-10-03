#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from dataclasses import dataclass, asdict
import struct
import time
from typing import Union
import serial
from xerxes_protocol.ids import DevId, MsgId
from xerxes_protocol.defaults import DEFAULT_BAUDRATE, DEFAULT_TIMEOUT


class ChecksumError(Exception): ...

class MessageIncomplete(Exception): ...

class InvalidMessage(Exception): ...

class LengthError(Exception): ...

class NetworkError(Exception): ...


def checksum(message: bytes) -> bytes:
    summary = sum(message)
    summary ^= 0xFF  # get complement of summary
    summary += 1  # get 2's complement
    summary %= 0x100  # get last 8 bits of summary
    return summary.to_bytes(1, "little")


class Addr(int):
    def __new__(cls, addr: Union[int, bytes]) -> None:
        if isinstance(addr, bytes):
            addr = int(addr.hex(), 16)

        assert isinstance(addr, int), f"address must be of type bytes|int, got {type(addr)} instead."
        assert addr >= 0, "address must be positive"
        assert addr < 256, "address must be lower than 256"

        return super().__new__(cls, addr)


    def to_bytes(self):
        return int(self).to_bytes(1, "little")


    def __bytes__(self):
        return self.to_bytes()


    def __repr__(self):
        return f"Addr(0x{self.to_bytes().hex()})"


    def __eq__(self, __o: object) -> bool:
        return int(self) == int(__o)


    def __hash__(self) -> int:
        return int(self)


@dataclass
class XerxesMessage:
    source: Addr
    destination: Addr
    length: int
    message_id: MsgId
    payload: bytes
    crc: int = 0
    

@dataclass
class XerxesPingReply:
    dev_id: DevId
    v_maj: int
    v_min: int
    latency: float

    def as_dict(self):
        return {
            "dev_id": str(self.dev_id),
            "version": f"{self.v_maj}.{self.v_min}",
            "latency": self.latency
        }


class FutureXerxesNetwork:
    def send_msg(self, __dst, __pld) -> None:
        raise NotImplementedError("You should assign real XerxesNetwork instead of FutureXN")
    
    
    def read_msg(self) -> None:
        raise NotImplementedError("You should assign real XerxesNetwork instead of FutureXN")
    
    
    def __repr__(self):
        return "FutureXerxesNetwork()"


class XerxesNetwork: ...


class XerxesNetwork:
    _ic = 0
    _instances = {}
    _opened = False

    def __init__(self, port: serial.Serial) -> None:
        assert isinstance(port, serial.Serial)
        self._s = port

    
    def init(self, baudrate: int = DEFAULT_BAUDRATE, timeout: float = DEFAULT_TIMEOUT) -> XerxesNetwork:
        self._s.baudrate = baudrate
        self._s.timeout = timeout
        
        # reopen the port with new settings
        self._s.close()
        if not self._s.isOpen():
            self._s.open()
        self._opened = True

        return self


    @property
    def opened(self) -> bool:
        return bool(self._opened)


    def __new__(cls: XerxesNetwork, port: str) -> XerxesNetwork:
        if port not in cls._instances.keys():
            cls._instances[port] = object.__new__(cls)

        return cls._instances[port]


    def __repr__(self) -> str:
        return f"XerxesNetwork(port={self._s})"


    def __del__(self):
        self._s.close()


    def read_msg(self) -> XerxesMessage:
        assert self._opened, "Serial port not opened yet. Call .init() first"

        # wait for start of message
        next_byte = self._s.read(1)
        while next_byte != b"\x01":
            next_byte = self._s.read(1)
            if len(next_byte)==0:
                raise TimeoutError("No message in queue")

        chs = 0x01
        # read message length
        msg_len = int(self._s.read(1).hex(), 16)
        chs += msg_len

        #read source and destination address
        src = self._s.read(1)
        dst = self._s.read(1)

        for i in [src, dst]:
            chs += int(i.hex(), 16) 

        # read message ID
        msg_id_raw = self._s.read(2)
        if(len(msg_id_raw)!=2):
            raise MessageIncomplete("Invalid message id received")
        for i in msg_id_raw:
            chs += i

        msg_id = struct.unpack("H", msg_id_raw)[0]

        # read and unpack all data into array, assuming it is uint32_t, little-endian
        raw_msg = bytes(0)
        for i in range(int(msg_len -    7)):
            next_byte = self._s.read(1)
            if(len(next_byte)!=1):
                raise MessageIncomplete("Received message incomplete")
            raw_msg += next_byte
            chs += int(next_byte.hex(), 16)
        
        #read checksum
        rcvd_chks = self._s.read(1)
        if len(rcvd_chks)!=1:
            raise MessageIncomplete("Received message incomplete")
        chs += int(rcvd_chks.hex(), 16)
        chs %= 0x100
        if chs:
            raise ChecksumError("Invalid checksum received")

        return XerxesMessage(
            source=Addr(src),
            destination=Addr(dst),
            length=msg_len,
            message_id=MsgId(msg_id),
            payload=raw_msg,
            crc=chs
        )
    
    
    def wait_for_reply(self, timeout: float) -> XerxesMessage:
        old_t = self._s.timeout
        self._s.timeout = timeout
        rply = self.read_msg()
        self._s.timeout = old_t
        return rply


    def send_msg(self, source: Addr, destination: Addr, payload: bytes) -> None:    
        assert self._opened, "Serial port not opened yet. Call .init() first"

        if not isinstance(destination, Addr):
            destination = Addr(destination)
        if not isinstance(source, Addr):
            source = Addr(source)
        assert isinstance(payload, bytes)
            
        SOH = b"\x01"

        msg = SOH  # SOH
        msg += (len(payload) + 5).to_bytes(1, "little")  # LEN
        msg += bytes(source) # FROM
        msg += bytes(destination) #  DST
        msg += payload
        msg += checksum(msg)
        self._s.write(msg)
