##!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Union
import math


class Id: ...


class Id:    
    def __init__(self, id: Union[int, bytes]) -> None:
        if isinstance(id, int):
            assert(id >= 0)
        elif isinstance(id, bytes):
            id = int(id.hex(), 16)
        else:
            raise TypeError(f"Unsupported argument, expected int|bytes, got {type(id)} instead")

        self._id : int = id


    def __bytes__(self) -> bytes:
        id: int = self._id
        byte_length = math.ceil(id.bit_length()/8)
        
        return id.to_bytes(byte_length, "little")
        

    def __repr__(self):
        return f"Id({bytes(self)})"
    
    
    def __int__(self):
        return int(self._id)
    

    def __str__(self):
        return f"Id({bytes(self).hex()})"


    def __eq__(self, __o: Id) -> bool:
        assert isinstance(__o, Id), f"Invalid object type received, expected {type(Id(0))}, got {type(__o)} instead."
        return self._id == __o._id


    def __hash__(self):
        return int(self._id)
        

class MsgIdMixin(Id):
    def __init__(self, id: Union[int, bytes]):
        if isinstance(id, bytes):
            assert len(id) == 2
        elif isinstance(id, int):
            assert id >= 0 and id <= 0xFFFF
        else:
            raise TypeError(f"Unsupported argument, expected int|bytes, got {type(id)} instead")
        super().__init__(id)
        
    
    def __bytes__(self):
        return self._id.to_bytes(2, "little")


    def __len__(self):
        return 2


class DevIdMixin(Id):
    def __init__(self, id: Union[int, bytes]):
        if isinstance(id, bytes):
            assert len(id) == 1
        elif isinstance(id, int):
            assert id >= 0 and id <= 0xFF
        else:
            raise TypeError(f"Unsupported argument, expected int|bytes, got {type(id)} instead")
        super().__init__(id)
    

    def __len__(self):
        return 1


class MsgId(MsgIdMixin):   
    # Ping packet
    PING                          = MsgIdMixin(0x0000)
    
    # Reply to ping packet
    PING_REPLY                    = MsgIdMixin(0x0001)
    
    # Acknowledge OK packet
    ACK_OK                        = MsgIdMixin(0x0002)
    
    # Acknowledge NOK packet
    ACK_NOK                       = MsgIdMixin(0x0003)
    
    RESET                         = MsgIdMixin(0x00FF)
    
    # Request to send measurements
    FETCH_MEASUREMENT             = MsgIdMixin(0x0100)
    
    # Synchronisaton message
    SYNC                          = MsgIdMixin(0x0101)
    
    # Set register to a value 
    # The message prototype is <MSGID_SET> <REG_ID> <LEN> <BYTE_1> ... <BYTE_N>
    WRITE                         = MsgIdMixin(0x0200)
    
    # Read  up to <LEN> bytes from device register, starting at <REG_ID>
    # The request prototype is <MSGID_READ> <REG_ID> <LEN>           
    READ_REQ                      = MsgIdMixin(0x0201)
    READ_REPLY                    = MsgIdMixin(0x0202)
    
    # Pressure value w/o temperature*/ 
    PRESSURE_Pa                   = MsgIdMixin(0x0400)
    
    STRAIN_24BIT                  = MsgIdMixin(0x1100)

    # Cutter 1000P/R, 63mm wheel */
    PULSES                        = MsgIdMixin(0x2A01)

    
    # 2 distance values, 0-22000um, no temp
    DISTANCE_22MM                 = MsgIdMixin(0x4000)
    # 2 distance values, 0-225000um, no temp
    DISTANCE_225MM                = MsgIdMixin(0x4100)
    

    # 2 angle values, X, Y (-90°, 90°)
    ANGLE_DEG_XY                  = MsgIdMixin(0x3000)


    def __repr__(self):
        return f"MsgId(0x{bytes(self).hex()})"


    def __str__(self):
        return self.__repr__()


class DevId(DevIdMixin):
    # Pressure sensors */
    # pressure sensor range 0-600mbar, output in Pa, 2 external temperature sensors -50/150°C output: mK */
    PRESSURE_600MBAR_2TEMP    = DevIdMixin(0x03)
    # pressure sensor range 0-60mbar, output in Pa, 2 external temperature sensors -50/150°C output: mK */
    PRESSURE_60MBAR_2TEMP     = DevIdMixin(0x04)
    
    # Strain sensors */
    # strain-gauge sensor range 0-2^24, 2 external temperature sensors -50/150°C output: mK */
    STRAIN_24BIT_2TEMP        = DevIdMixin(0x11)
    
    # I/O Devices */
    # I/O device, 8DI/8DO (8xDigital Input, 8xDigital 0utput) */
    IO_8DI_8DO                = DevIdMixin(0x20)
    
    
    # Inclinometers and accelerometers */
    # Inclinometer SCL3300 */
    ANGLE_XY_90               = DevIdMixin(0x30)
    
    
    # Distance sensors */
    # Distance sensor 0-22mm, resistive, linear*/
    DIST_22MM                 = DevIdMixin(0x40)
    # Distance sensor 0-225mm, resistive, linear*/
    DIST_225MM                = DevIdMixin(0x41)
    
    
    # Encoder reader */
    DEVID_ENC_1000PPR         = DevIdMixin(0x2A)


    def __repr__(self):
        return f"DevId(0x{bytes(self).hex()})"
    
    
    def __str__(self):
        return self.__repr__()