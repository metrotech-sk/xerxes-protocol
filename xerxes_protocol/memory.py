from dataclasses import dataclass
import struct
from typing import List, Union, Callable


# non-volatile memory map (persistent)
# memory offset of the offset of the process values
GAIN_PV0_OFFSET = 0
GAIN_PV1_OFFSET = 4
GAIN_PV2_OFFSET = 8
GAIN_PV3_OFFSET = 12

# memory offset of the offset of the process values
OFFSET_PV0_OFFSET = 16
OFFSET_PV1_OFFSET = 20
OFFSET_PV2_OFFSET = 24
OFFSET_PV3_OFFSET = 28

# memory offset of cycle time in microseconds (4 bytes)
OFFSET_DESIRED_CYCLE_TIME = 32

OFFSET_CONFIG_BITS = 40
OFFSET_ADDRESS = 44

# Volatile range (not persistent)
PV0_OFFSET = 256
PV1_OFFSET = 260
PV2_OFFSET = 264
PV3_OFFSET = 268

MEAN_PV0_OFFSET = 272
MEAN_PV1_OFFSET = 276
MEAN_PV2_OFFSET = 280
MEAN_PV3_OFFSET = 284

STDDEV_PV0_OFFSET = 288
STDDEV_PV1_OFFSET = 292
STDDEV_PV2_OFFSET = 296
STDDEV_PV3_OFFSET = 300

MIN_PV0_OFFSET = 304
MIN_PV1_OFFSET = 308
MIN_PV2_OFFSET = 312
MIN_PV3_OFFSET = 316

MAX_PV0_OFFSET = 320
MAX_PV1_OFFSET = 324
MAX_PV2_OFFSET = 328
MAX_PV3_OFFSET = 332

DV0_OFFSET = 336
DV1_OFFSET = 340
DV2_OFFSET = 344
DV3_OFFSET = 348

MEM_UNLOCKED_OFFSET = 384

# Read only range
STATUS_OFFSET = 512
ERROR_OFFSET = 520
UID_OFFSET = 528

OFFSET_NET_CYCLE_TIME = 544


@dataclass
class ElementType:
    """Represents a memory type in memory.
    
    Attributes:
        _container (bytes | int | float | bool): The container type of the memory type.
        _format (str): The format of the memory type. See struct module for more information.
        _length (int): The length of the memory type in bytes.
    """

    _container: bytes | int | float | bool
    _format: str
    _length: int


class uint64_t(ElementType):
    """Represents a 64 bit unsigned integer in memory."""

    _container = int
    _format = "Q"
    _length = 8


class ull(uint64_t):
    """Represents a 64 bit unsigned integer in memory."""


class uint32_t(ElementType):
    """Represents a 32 bit unsigned integer in memory."""

    _container = int
    _format = "I"
    _length = 4


class ul(uint32_t):
    """Represents a 32 bit unsigned integer in memory."""


class int32_t(ElementType):
    """Represents a 32 bit signed integer in memory."""

    _container = int
    _format = "i"
    _length = 4


class int(int32_t):
    """Represents a 32 bit signed integer in memory."""


class uint16_t(ElementType):
    """Represents a 16 bit unsigned integer in memory."""

    _container = int
    _format = "H"
    _length = 2


class ushort(uint16_t):
    """Represents a 16 bit unsigned integer in memory."""


class uint8_t(ElementType):
    """Represents a 8 bit unsigned integer in memory."""

    _container = int
    _format = "B"
    _length = 1


class uchar(uint8_t):
    """Represents a 8 bit unsigned integer in memory."""


class float_t(ElementType):
    """Represents a 32 bit float in memory."""

    _container = float
    _format = "f"
    _length = 4


class double_t(ElementType):
    """Represents a 64 bit float in memory."""

    _container = float
    _format = "d"
    _length = 8


@dataclass
class MemoryElement:
    """Represents a memory element in the Xerxes memory map."""
    mem_addr: int
    mem_type: ElementType
    write_access: bool = True

    def can_write(self) -> bool:
        """Returns whether the memory element can be written to."""
        return self.write_access


class XerxesMemoryType:
    """Represents a memory access type in the Xerxes memory map
    
    Attributes:
        __read_reg_f (Callable[[int, int], bytes]): 
            The function to read a register. The first argument is the address and the second argument is the length.
            Should return the data as bytes.
        __write_reg_f (Callable[[int, bytes], bool]):
            The function to write a register. The first argument is the address and the second argument is the data.
            Should return True if the write was successful.
    """

    __read_reg_f: Callable[[int, int], bytes]
    __write_reg_f: Callable[[int, bytes], bool]


    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join([f'{k}={v}' for k, v in self.__dict__.items()])})"
    

    def __read_mem_elem(self, mem_elem: MemoryElement) -> float | int:
        """Reads a memory element from the Xerxes memory map."""

        # read the memory element - the result is a bytes object
        _r = self.__read_reg_f(mem_elem.mem_addr, mem_elem.mem_type._length)

        # unpack the bytes object into a tuple
        return struct.unpack(mem_elem.mem_type._format, _r)[0]


    def __write_mem_elem(self, mem_elem: MemoryElement, value: float | int):
        """Writes a memory element to the Xerxes memory map."""

        # pack the value into a bytes object
        _bv = struct.pack(mem_elem.mem_type._format, value)

        # write the bytes object to the memory element
        self.__write_reg_f(mem_elem.mem_addr, _bv)


    def __init__(self, _read_reg_f: Callable, _write_reg_f: Callable):
        self.__read_reg_f = _read_reg_f
        self.__write_reg_f = _write_reg_f


        for key in dir(self.__class__):
            if key.startswith("__"):
                continue

            attr = getattr(self, key)
            # construct getter and setter
            if isinstance(attr, MemoryElement):
                # key is for example: _gain_pv0
                # attr is for example: MemoryElement(0, float_t)

                def make_fget(_attr):
                    # define dynamic getter
                    def fget(self):
                        return self.__read_mem_elem(_attr)
                    return fget
                
                def make_fset(_attr):
                    # define dynamic setter
                    def setter(self, value):
                        assert isinstance(value, _attr.mem_type._container), \
                            f"Value must be of type {_attr.mem_type._container}"
                        
                        if not self.__write_mem_elem(_attr, value):
                            raise RuntimeError("Failed to write to memory element")
                    return setter

                # set the getter and setter
                setattr(
                    self.__class__, 
                    key.lstrip("_"), 
                    property(make_fget(attr), make_fset(attr) if attr.can_write() else None)
                )


class MemoryNonVolatile(XerxesMemoryType):
    _gain_pv0 = MemoryElement(GAIN_PV0_OFFSET, float_t)
    _gain_pv1 = MemoryElement(GAIN_PV1_OFFSET, float_t)
    _gain_pv2 = MemoryElement(GAIN_PV2_OFFSET, float_t)
    _gain_pv3 = MemoryElement(GAIN_PV3_OFFSET, float_t)

    _offset_pv0 = MemoryElement(OFFSET_PV0_OFFSET, float_t)
    _offset_pv1 = MemoryElement(OFFSET_PV1_OFFSET, float_t)
    _offset_pv2 = MemoryElement(OFFSET_PV2_OFFSET, float_t)
    _offset_pv3 = MemoryElement(OFFSET_PV3_OFFSET, float_t)

    _desired_cycle_time = MemoryElement(OFFSET_DESIRED_CYCLE_TIME, uint32_t)
    _device_address = MemoryElement(OFFSET_ADDRESS, uint8_t)
    _config = MemoryElement(OFFSET_CONFIG_BITS, uint8_t)
    _net_cycle_time_us = MemoryElement(OFFSET_NET_CYCLE_TIME, uint32_t)
    

class MemoryVolatile(XerxesMemoryType):
    _pv0 = MemoryElement(PV0_OFFSET, float_t)
    _pv1 = MemoryElement(PV1_OFFSET, float_t)
    _pv2 = MemoryElement(PV2_OFFSET, float_t)
    _pv3 = MemoryElement(PV3_OFFSET, float_t)

    _mean_pv0 = MemoryElement(MEAN_PV0_OFFSET, float_t)
    _mean_pv1 = MemoryElement(MEAN_PV1_OFFSET, float_t)
    _mean_pv2 = MemoryElement(MEAN_PV2_OFFSET, float_t)
    _mean_pv3 = MemoryElement(MEAN_PV3_OFFSET, float_t)

    _std_dev_pv0 = MemoryElement(STDDEV_PV0_OFFSET, float_t)
    _std_dev_pv1 = MemoryElement(STDDEV_PV1_OFFSET, float_t)
    _std_dev_pv2 = MemoryElement(STDDEV_PV2_OFFSET, float_t)
    _std_dev_pv3 = MemoryElement(STDDEV_PV3_OFFSET, float_t)

    _min_pv0 = MemoryElement(MIN_PV0_OFFSET, float_t)
    _min_pv1 = MemoryElement(MIN_PV1_OFFSET, float_t)
    _min_pv2 = MemoryElement(MIN_PV2_OFFSET, float_t)
    _min_pv3 = MemoryElement(MIN_PV3_OFFSET, float_t)

    _max_pv0 = MemoryElement(MAX_PV0_OFFSET, float_t)
    _max_pv1 = MemoryElement(MAX_PV1_OFFSET, float_t)
    _max_pv2 = MemoryElement(MAX_PV2_OFFSET, float_t)
    _max_pv3 = MemoryElement(MAX_PV3_OFFSET, float_t)

    _dv0 = MemoryElement(DV0_OFFSET, uint32_t)
    _dv1 = MemoryElement(DV1_OFFSET, uint32_t)
    _dv2 = MemoryElement(DV2_OFFSET, uint32_t)
    _dv3 = MemoryElement(DV3_OFFSET, uint32_t)

    _memory_lock = MemoryElement(MEM_UNLOCKED_OFFSET, uint32_t)


class MemoryReadOnly(XerxesMemoryType):
    _status = MemoryElement(STATUS_OFFSET, uint64_t, write_access=False)
    _error = MemoryElement(ERROR_OFFSET, uint64_t, write_access=False)
    _uid = MemoryElement(UID_OFFSET, uint64_t, write_access=False)


class XerxesMemoryMap(MemoryNonVolatile, MemoryVolatile, MemoryReadOnly):
    """Xerxes memory map class.
    
    This class is used to access the memory of the Xerxes device.
    
    The memory map is split into three classes:
    - MemoryNonVolatile: contains the non-volatile memory elements - these
        elements are stored in the EEPROM of the Xerxes device
    - MemoryVolatile: contains the volatile memory elements - these elements
        are stored in the RAM of the Xerxes device
    - MemoryReadOnly: contains the read-only memory elements - these elements
        are stored in the RAM of the Xerxes device and can only be read
    """
