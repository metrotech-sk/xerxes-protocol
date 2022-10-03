#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class Unit:
    _value = 0

    def __init__(self, value=0):
        self._value = value

    def preferred(self):
        return self._value
    
    @property
    def value(self):
        return self._value
    
    def __repr__(self):
        return f"Unit({self._value})"

    def __radd__(self, other):
        return self._value + other

    def __add__(self, other):
        return self._value + other

    def __sub__(self, other):
        return self._value - other
    
    def __rsub__(self, other):
        return other - self._value


class Index(Unit): ...