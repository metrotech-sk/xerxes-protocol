#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass
import struct
from typing import Union, Any, List
import time

from xerxes_protocol.ids import DevId, MsgId
from xerxes_protocol.network import Addr, InvalidMessage, XerxesMessage, XerxesPingReply
from xerxes_protocol.hierarchy.root import XerxesRoot
from xerxes_protocol.units.unit import Unit
from xerxes_protocol.memory import (
    XerxesMemoryMap,
    MemoryElement
)

__author__ = "theMladyPan"
__version__ = "1.4.0"
__license__ = "MIT"
__email__ = "stanislav@rubint.sk"
__status__ = "Production"
__package__ = "xerxes_protocol"
__date__ = "2023-02-22"

__all__ = [
    "LeafConfig",
    "LeafData",
    "Leaf"
]


@dataclass
class LeafConfig:
    """Enumeration of all leaf configuration flags.

    This class is an enumeration of all leaf configuration flags. It is used to
    represent the configuration of a leaf in a convenient way.

    Attributes:
        freeRun (int): The free run flag.
        calcStat (int): The calculate statistics flag.
    
    Example:
        >>> leaf = Leaf(Addr(1), XerxesNetwork())
        >>> leaf.config = LeafConfig.freeRun | LeafConfig.calcStat
        >>> print(leaf.config)
        3
    """

    freeRun: int = 1
    calcStat: int = 1 << 1


@dataclass
class LeafData(object):
    """Base class for all leaf data classes.
    
    This class is the base class for all leaf data classes. It is used to
    represent the data of a leaf in a convenient way.
    """

    def _as_dict(self):
        """Return a dictionary representation of the data."""
        d = {}

        # for every attribute in the class
        for attribute in self.__dir__():

            # if the attribute is not a private attribute
            if not attribute.startswith("_"):
                
                # get value of the attribute
                attr_val = self.__getattribute__(attribute)

                # if the attribute is basic datatype
                if isinstance(attr_val, (int, float, str, dict, list)):
                    d.update({
                        attribute: attr_val
                    })
                
                # if the attribute is a unit
                elif isinstance(attr_val, Unit):
                    d.update({
                        attribute: attr_val.preferred()
                    })
                    
        return d


class Leaf:
    """Base class for all leaf classes.

    This class is the base class for all leaf classes. It is used to represent
    a leaf in a convenient way.

    Args:
        addr (Addr): The address of the leaf.
        root (XerxesRoot): The root node of the network.
    
    Attributes:
        _address (Addr): The address of the leaf.
        _memory_map (XerxesMemoryMap): The memory map of the leaf.
        root (XerxesRoot): The root node of the network.
    """
    

    _memory_map = XerxesMemoryMap()


    def __init__(self, addr: Addr, root: XerxesRoot):
        # try to convert addr to Addr if it is an integer
        if isinstance(addr, int):
            addr = Addr(addr)
        
        # check if addr is an Addr
        assert isinstance(addr, Addr), f"Address must be of type int or Addr, got {type(addr)} instead."
        assert isinstance(root, XerxesRoot), f"Root must be of type XerxesRoot, got {type(root)} instead."
        self._address = addr

        self.root: XerxesRoot
        self.root = root
         
        # create convenient access method for memory map
        for key in dir(self._memory_map):
            # skip private attributes
            if key.startswith("_"):
                continue
            
            attr: Any | MemoryElement = getattr(self._memory_map, key)
            # if attribute is a memory element, create a convenient access method for it
            if isinstance(attr, MemoryElement):
                # key is for example: "gain_pv0"
                # attr is for example: MemoryElement(0, float_t)

                # define dynamic getter
                def make_fget(_attr: MemoryElement):
                    def fget(self):
                        # read the memory element - the result is a bytes object
                        _r = self.read_reg_net(_attr.elem_addr, _attr.elem_type._length)

                        # unpack the bytes object into a tuple
                        return struct.unpack(_attr.elem_type._format, _r)[0]
                    return fget

                # define dynamic setter
                def make_fset(_attr: MemoryElement):
                    def setter(self, value):
                        assert (
                            isinstance(value, int) or 
                            isinstance(value, float)
                        ), f"Value must be of type float or int, got {type(value)} instead."

                        # check if memory element is writable
                        assert _attr.write_access, "Memory element is not writable."

                        # pack the value into a bytes object, using the format of the memory element
                        _bv = struct.pack(_attr.elem_type._format, value)

                        # write the bytes object to the memory element
                        if not self.write_reg_net(_attr.elem_addr, _bv):
                            raise RuntimeError("Failed to write to memory element")
                    return setter

                # set the getter and setter as properties
                setattr(
                    self.__class__, 
                    key, 
                    property(
                        make_fget(attr), 
                        make_fset(attr)
                    )
                )


    def ping(self) -> XerxesPingReply:
        """Pings the leaf. Returns the reply. See XerxesRoot.ping for more information."""
        return self.root.ping(bytes(self.address))


    def exchange(self, payload: bytes) -> XerxesMessage:
        """Sends a message to the leaf and returns the reply.

        Args:
            payload (bytes): The payload of the message.

        Returns:
            XerxesMessage: The message received from the leaf.
        """

        if not isinstance(payload, bytes):
            try:
                payload = bytes(payload)
            finally:
                pass
        # test if payload is list of uchars
        assert isinstance(payload, bytes)
        self.root.send_msg(self._address, payload)
        return self.root.network.read_msg()
            
    
    def read_reg_net(self, reg_addr: int, length: int) -> bytes:
        """Encapsulates the read_reg method to return only the payload."""

        return self.read_reg(reg_addr, length).payload
    

    def read_reg(self, reg_addr: int, length: int) -> XerxesMessage:
        """Reads a register from the leaf.

        Args:
            reg_addr (int): The address of the register.
            length (int): The length of the register in bytes.

        Returns:
            XerxesMessage: The message received from the leaf.
        """

        length = int(length)
        reg_addr = int(reg_addr)
        payload = bytes(MsgId.READ_REQ) + reg_addr.to_bytes(2, "little") + length.to_bytes(1, "little")
        return self.exchange(payload)
    
    
    def write_reg(self, reg_addr: int, value: bytes) -> XerxesMessage:
        """Writes a register to the leaf.
        
        Args:
            reg_addr (int): The address of the register.
            value (bytes): The value to write to the register.
        
        Returns:
            XerxesMessage: The message received from the leaf.
        """

        reg_addr = int(reg_addr)
        payload = bytes(MsgId.WRITE) + reg_addr.to_bytes(2, "little") + value
        
        self.root.send_msg(self._address, payload)
        reply = self.root.network.wait_for_reply(0.01 * len(payload))  # it takes ~10ms for byte to be written to memory
        return reply
    

    def write_reg_net(self, reg_addr: int, value: bytes) -> bool:
        """Encapsulates the write_reg method to return only the payload."""

        return self.write_reg(reg_addr, value).message_id == MsgId.ACK_OK
    

    def reset_soft(self) -> None:
        """Restarts the leaf."""

        self.root.send_msg(self._address, bytes(MsgId.RESET_SOFT))


    @property
    def address(self) -> Addr:
        return self._address


    @address.setter
    def address(self, _addr: int) -> None:
        assert (
            isinstance(_addr, int)
        ), f"Address must be of type int, got {type(_addr)} instead."

        try:
            # try to set the address to the new value
            self.address = int(_addr)
            # if the address was set, set the address property to the new value
            self._address = Addr(_addr)

        except ValueError:
            raise ValueError(f"Address must be of type int, got {type(_addr)} instead.")
        
        except AttributeError:
            raise AttributeError("Address can not be set right now.")

        except TimeoutError:
            raise TimeoutError("Timed out while setting address. Nothing was written to the leaf.")
        

    def __repr__(self) -> str:
        return f"Leaf(addr={self.address}, root={self.root})"


    def __str__(self) -> str:
        return self.__repr__()


    @staticmethod
    def average(array: List[LeafData]) -> LeafData:
        """Returns the average of a list of leaf data objects.

        Args:
            array (List[LeafData]): The list of leaf data objects.

        Returns:
            LeafData: The average of the list of leaf data objects.
        """

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
                average_class.__setattr__(key, sum(averages) / len(averages))
        return average_class


    def __eq__(self, __o: object) -> bool:
        """Returns True if the addresses of the two leaves are equal therefore they are the same leaf."""

        return isinstance(__o, Leaf) and self._address == __o.address

    
    def __hash__(self) -> int:
        """Returns the hash of the address of the leaf - unique for each leaf."""
        return hash(self.address)
