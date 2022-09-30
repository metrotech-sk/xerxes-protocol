import pytest
import serial
import os


@pytest.fixture
def com_port() -> serial.Serial:
    if os.name == "nt":
        # som na windows
        port = "COM14"
    else:
        # on linux machine:
        port = "/dev/ttyUSB0"
    
    try:
        com = serial.Serial(port=port, baudrate=115200, timeout=0.02)
        yield com
        com.close()
    except serial.SerialException:
        yield None
    
        