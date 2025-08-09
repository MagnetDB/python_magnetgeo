# File: new-tests/test_probe_integration.py
import pytest
import json
import yaml
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import Mock

# Import all classes for testing
from python_magnetgeo.Insert import Insert
from python_magnetgeo.Helix import Helix
from python_magnetgeo.Ring import Ring
from python_magnetgeo.Supra import Supra
from python_magnetgeo.Supras import Supras
from python_magnetgeo.Bitter import Bitter
from python_magnetgeo.Bitters import Bitters
from python_magnetgeo.Screen import Screen
from python_magnetgeo.MSite import MSite
from python_magnetgeo.Probe import Probe
from python_magnetgeo.Shape import Shape
from python_magnetgeo.ModelAxi import ModelAxi
from python_magnetgeo.Model3D import Model3D

class TestProbeIntegration:
    """Test probe system integration with magnet classes"""

    def test_insert_with_probes(self, sample_insert):
        """Test Insert properly handles probe collections"""
        assert len(sample_insert.probes) == 1
        assert isinstance(sample_insert.probes[0], Probe)
        assert sample_insert.probes[0].name == "test_probe"

    def test_insert_probe_serialization(self, sample_insert):
        """Test Insert serialization includes probes"""
        json_str = sample_insert.to_json()
        parsed = json.loads(json_str)
        
        assert "probes" in parsed
        assert len(parsed["probes"]) == 1

    def test_supras_with_probes(self, sample_supra, sample_probe):
        """Test Supras collection with probe integration"""
        supras = Supras(
            name="probe_supras",
            magnets=[sample_supra],
            innerbore=15.0,
            outerbore=50.0,
            probes=[sample_probe]
        )
        
        assert len(supras.probes) == 1
        assert supras.probes[0].probe_type == "voltage_taps"

    def test_probe_string_references(self):
        """Test probe collections can handle string references"""
        insert = Insert(
            name="string_probe_insert",
            helices=["helix1"],
            rings=["ring1"],
            currentleads=[],
            hangles=[],
            rangles=[],
            innerbore=5.0,
            outerbore=25.0,
            probes=["probe_ref1", "probe_ref2"]  # String references
        )
        
        assert insert.probes == ["probe_ref1", "probe_ref2"]

    def test_empty_probe_collections(self):
        """Test classes handle empty probe collections properly"""
        insert = Insert(
            name="empty_probes",
            helices=[],
            rings=[],
            currentleads=[],
            hangles=[],
            rangles=[],
            innerbore=1.0,
            outerbore=10.0,
            probes=[]
        )
        
        assert insert.probes == []
        assert len(insert.probes) == 0


