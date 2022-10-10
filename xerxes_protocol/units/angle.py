#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from math import pi
from .unit import Unit

class Angle(Unit):
    @property
    def degrees(self):
        return 180*self.value/pi

    @property
    def rad(self):
        return self.value
    
    @staticmethod
    def from_degrees(deg):
        return Angle(pi*deg/180)

    def __repr__(self):
        return f"Angle({self.value})"
    
    def preferred(self):
        return self.degrees