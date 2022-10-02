#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from xerxes_protocol.units.unit import Unit

class Pressure(Unit):
    @property
    def mmH2O(self):
        return self._value * 0.10197162129779283

    @property
    def bar(self):
        return self._value * 0.00001

    @property
    def Pascal(self):
        return self.value
    
    @staticmethod
    def from_micro_bar(ubar):
        return Pressure(ubar/10)

    def __repr__(self):
        return f"Pressure({self.value})"

    @property
    def preferred(self):
        return self.Pascal