#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
HTS (High-Temperature Superconductor) Insert Geometry Package

This package provides modular classes for modeling HTS insert structures:

Hierarchy:
    Tape (leaf) - HTS tape geometry
    Isolation (leaf) - Isolation layer structure
    ↓
    Pancake - Single pancake coil (depends on Tape)
    ↓
    DoublePancake - Two pancakes with isolation (depends on Pancake + Isolation)
    ↓
    HTSInsert - Complete HTS insert (depends on DoublePancake + Isolation)

Classes:
    Tape: HTS tape with width, height, and duromag thickness
    Isolation: Multi-layer isolation structure
    Pancake: Single pancake coil with tape windings
    DoublePancake: Two pancakes separated by isolation
    HTSInsert: Complete HTS insert with multiple double pancakes

Units:
    All dimensions in millimeters (mm) unless otherwise specified.
    The Supra class handles conversion to meters for electromagnetics.

Example:
    >>> from python_magnetgeo.hts import Tape, Pancake, HTSInsert
    >>> 
    >>> # Create tape
    >>> tape = Tape(w=12.0, h=0.1, e=0.05)
    >>> 
    >>> # Create pancake
    >>> pancake = Pancake(r0=50.0, n=100, mandrin=2.0, tape=tape)
    >>> 
    >>> # Load complete insert from YAML
    >>> insert = HTSInsert.from_yaml("my_insert.yaml")

Migration from SupraStructure.py:
    - tape → Tape
    - isolation → Isolation
    - pancake → Pancake
    - dblpancake → DoublePancake
    - HTSinsert → HTSInsert (minimal change)
    - from_data() → from_dict()
    - getH() → height property
    - getW() → width property
    - JSON configs → YAML configs
"""

from .tape import Tape
from .isolation import Isolation
from .pancake import Pancake
from .double_pancake import DoublePancake
from .hts_insert import HTSInsert

# Public API
__all__ = [
    'Tape',
    'Isolation',
    'Pancake',
    'DoublePancake',
    'HTSInsert',
]

# Version info
__version__ = '0.8.0'
