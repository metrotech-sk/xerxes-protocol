#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .pressure import Pressure

class Nivelation(Pressure):
    def __init__(self, value=0, conv_func=lambda x : x):
        self._conversion = conv_func
        super().__init__(value)

    @property
    def mm(self):
        converted = self._conversion(self.value)
        return converted

    def preferred(self):
        return self.mm

    def __repr__(self) -> str:
        return f"Nivelation({self._value})"
