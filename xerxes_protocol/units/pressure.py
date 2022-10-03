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

    def preferred(self):
        return self.Pascal


def Pascal(Pa) -> Pressure:
    return Pressure(Pa)


_g = 9.80665


class Nivelation(Pressure):
    def mm_ethyleneglycol(self):
        return self.value/(_g*1.1132)

    def mm_water(self):
        return self.value/(_g*1)

    def mm_siloxane(self):
        return self.value/(_g*0.965)
    
    def mm_propyleneglycol(self):
        return self.value/(_g*1.04)

    def preferred(self):
        return self.mm_propyleneglycol()