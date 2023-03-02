#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from xerxes_protocol import (
    Leaf,
    XerxesNetwork,
    XerxesRoot,
    LeafConfig
)
from serial import Serial
import time

xn = XerxesNetwork(Serial("/dev/ttyUSB0", 115200))
xn.init(timeout=0.01)
xr = XerxesRoot(0x1E, xn)


def address_config():
    print("looking for leafs...")
    for i in range(0, 254):
        try:
            print(f"{i}", end=", ", flush=True)
            leaf = Leaf(i, xr)
            leaf.ping()
            break
        except TimeoutError:
            pass
    print(f"Ping: {leaf.ping()}")
    print(f"Address: {leaf.device_address}")
    print(f"Config: {leaf.device_config}")
    print(f"device_uid: {leaf.device_uid}")
    
    new_addr = int(input("New address: "))
    leaf.address = new_addr    
    assert leaf.device_address == new_addr
    print(f"Address changed to: {leaf.device_address}")
    enable_freerun = input("Enable freerun? (y/n): ").lower() == "y"
    enable_stat = input("Enable statistic? (y/n): ").lower() == "y"
    config = LeafConfig.freeRun if enable_freerun else 0
    config |= LeafConfig.calcStat if enable_stat else 0
    leaf.device_config = config
    assert leaf.device_config == config
    print(f"Config changed to: {leaf.device_config}")
        

if __name__ == "__main__":
    while True:
        try:
            address_config()
            time.sleep(1)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(e)
            time.sleep(1)