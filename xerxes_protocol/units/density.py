#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .unit import Unit

class Fraction(Unit):
    """Unit of fraction, where 0 is none and 1 complete saturation

    Args:
        Unit (float): enter direct fraction of component or use static generators 'from_ppm(ppm)' or 'from_percent(percent)'        

    """
    @property
    def ppm(self):
        """Return Fraction in parts per million

        Returns:
            float: parts per million
        """
        return self.value * 1_000_000

    @property
    def percent(self):
        return self.value * 100.0

    def __repr__(self):
        return f"PPM({self.value})"
    
    
    def preferred(self):
        return self.value
    
    @staticmethod
    def from_ppm(_v):
        return Fraction(
            value=_v / 1_000_000
        )

    @staticmethod
    def from_percent(_v):
        return Fraction(
            value=_v / 100
        )


class Density(Unit):
    @property
    def ug_per_m3(self):
        return self.value * 1_000_000_000

    @property
    def kg_per_m3(self):
        return self.value

    def __repr__(self):
        return f"Density({self.value})"

    @property
    def preferred(self):
        return self.kg_per_m3

    @staticmethod
    def from_ug_per_m3(_v):
        return Density(value=_v/1_000_000_000)