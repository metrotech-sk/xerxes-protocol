#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .unit import Unit

class Length(Unit):
    @property
    def m(self):
        return self.value

    @property
    def mm(self):
        return self.value * 1000.0

    def __repr__(self):
        return f"Length({self.value})"

    def preferred(self):
        return self.m