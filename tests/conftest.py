#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Pytest configuration file for Probe class tests
"""

import pytest
import sys
import os

# Add the parent directory to Python path so we can import from python_magnetgeo
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def sample_voltage_probes():
    """Fixture providing sample voltage probe data"""
    from python_magnetgeo.Probe import Probe
    return Probe(
        name="fixture_voltage",
        probe_type="voltage_taps",
        index=["V1", "V2", "V3", "V4"],
        locations=[
            [10.5, 0.0, 15.2],
            [12.3, 0.0, 18.7],
            [14.1, 0.0, 22.1],
            [15.9, 0.0, 25.6]
        ]
    )

@pytest.fixture
def sample_temperature_probes():
    """Fixture providing sample temperature probe data"""
    from python_magnetgeo.Probe import Probe
    return Probe(
        name="fixture_temperature",
        probe_type="temperature",
        index=[1, 2, 3],
        locations=[
            [11.0, 5.2, 16.5],
            [13.5, -3.1, 20.0],
            [16.2, 2.7, 24.8]
        ]
    )

@pytest.fixture
def sample_field_probes():
    """Fixture providing sample magnetic field probe data"""
    from python_magnetgeo.Probe import Probe
    return Probe(
        name="fixture_field",
        probe_type="magnetic_field",
        index=["Bz_center", "Br_edge"],
        locations=[
            [0.0, 0.0, 0.0],
            [5.0, 0.0, 0.0]
        ]
    )
