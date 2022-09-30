import pytest
from xerxes_protocol.network import checksum

def test_checksum_1():
    assert checksum(b"1A2B3C4D5E6F") == b"6"