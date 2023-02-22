import pytest
import serial
from xerxes_protocol.memory import (
    ElementType,
    uint64_t,
    ull,
    uint32_t,
    ul,
    uint16_t,
    ushort,
    uint8_t,
    uchar,
    float_t,
    double_t,
    MemoryNonVolatile,
    MemoryVolatile,
    MemoryReadOnly,
    MemoryElement,
    XerxesMemoryMap
)
from xerxes_protocol.hierarchy.leaves.leaf import LeafData, Leaf
from xerxes_protocol import Addr, XerxesRoot, XerxesNetwork


@pytest.fixture
def XN() -> XerxesNetwork:
    """Prepare Xerxes network to test with.

    Returns:
        XerxesNetwork: Xerxes network to test with.
    """
    com: serial.Serial = serial.Serial("/dev/ttyUSB0", 115200, timeout=0.01)
    XN = XerxesNetwork(com)
    XN.init(timeout=0.01)
    return XN


@pytest.fixture(autouse=True)
def XR(XN: XerxesNetwork) -> XerxesRoot:
    """Prepare Xerxes root to test with.

    Args:
        XN (XerxesNetwork): Xerxes network to test with.

    Returns:
        XerxesRoot: Xerxes root to test with.
    """
    XR = XerxesRoot(0x1E, XN)
    return XR


class TestElemType:
    def test_memory_type_valid(self):
        m_byte = ElementType(_format="B", _length=1, _container=int)
        assert m_byte._format == "B"
        assert m_byte._length == 1
        assert m_byte._container == int


    def test_memory_type_invalid(self):
        with pytest.raises(AssertionError):
            ElementType(_format="c", _length=1, _container=int)


    def test_memory_type_defaults(self):
        assert uint64_t._length == 8
        assert uint64_t._format == "Q"
        assert uint64_t._container == int

        assert uint32_t._length == 4
        assert uint32_t._format == "I"
        assert uint32_t._container == int

        assert uint16_t._length == 2
        assert uint16_t._format == "H"
        assert uint16_t._container == int

        assert uint8_t._length == 1
        assert uint8_t._format == "B"
        assert uint8_t._container == int

        assert float_t._length == 4
        assert float_t._format == "f"
        assert float_t._container == float

        assert double_t._length == 8
        assert double_t._format == "d"
        assert double_t._container == float
    

    def test_memory_element(self):
        me = MemoryElement(0, uint64_t, 0)
        print(me)


class TestVolatileMemory:
    def test_volatile_memory(self, XR: XerxesRoot):
        leaf = Leaf(Addr(0), XR)
        print(leaf._memory_map.pv0)
        print(leaf.read_param("pv0"))
