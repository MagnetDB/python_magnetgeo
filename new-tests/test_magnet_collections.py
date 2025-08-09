# File: new-tests/test_magnet_collections.py
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

class TestMagnetCollections:
    """Test magnet collection classes (Insert, Supras, Bitters, MSite)"""

    def test_insert_get_nhelices(self, sample_insert):
        """Test Insert helix counting"""
        count = sample_insert.get_nhelices()
        assert count == 1

    def test_insert_with_string_references(self):
        """Test Insert with string references instead of objects"""
        insert = Insert(
            name="string_insert",
            helices=["helix1", "helix2", "helix3"],
            rings=["ring1", "ring2"],
            currentleads=["inner", "outer"],
            hangles=[0.0, 90.0, 180.0, 270.0],
            rangles=[45.0, 135.0, 225.0, 315.0],
            innerbore=12.0,
            outerbore=40.0,
            probes=[]
        )
        
        assert insert.get_nhelices() == 3
        assert len(insert.rings) == 2
        assert len(insert.currentleads) == 2

    def test_supras_collection(self, sample_supra):
        """Test Supras collection functionality"""
        supra2 = Supra("supra2", [45.0, 65.0], [95.0, 175.0], 3, "BSCCO")
        
        supras = Supras(
            name="test_supras_collection",
            magnets=[sample_supra, supra2],
            innerbore=18.0,
            outerbore=70.0,
            probes=[]
        )
        
        assert supras.name == "test_supras_collection"
        assert len(supras.magnets) == 2
        assert supras.innerbore == 18.0
        assert supras.outerbore == 70.0

    def test_supras_bounding_box(self):
        """Test Supras boundingBox encompasses all magnets"""
        supra1 = Supra("s1", [10.0, 20.0], [0.0, 50.0], 2, "LTS")
        supra2 = Supra("s2", [25.0, 35.0], [30.0, 80.0], 3, "HTS")
        
        supras = Supras("bbox_supras", [supra1, supra2], 5.0, 40.0, [])
        rb, zb = supras.boundingBox()
        
        # Should encompass both supras
        assert rb[0] <= 10.0  # min of both
        assert rb[1] >= 35.0  # max of both  
        assert zb[0] <= 0.0   # min of both
        assert zb[1] >= 80.0  # max of both

    def test_msite_initialization(self, sample_insert):
        """Test MSite with magnet collections"""
        msite = MSite(
            name="test_msite",
            magnets=[sample_insert],
            screens=None,
            z_offset=None,
            r_offset=None,
            paralax=None
        )
        
        assert msite.name == "test_msite"
        assert len(msite.magnets) == 1
        assert msite.screens is None

    def test_msite_with_screens(self, sample_insert):
        """Test MSite with screen objects"""
        screen = Screen("msite_screen", [0.0, 60.0], [0.0, 200.0])
        
        msite = MSite(
            name="msite_with_screens",
            magnets=[sample_insert],
            screens=[screen],
            z_offset=[0.0],
            r_offset=[0.0],
            paralax=[0.0]
        )
        
        assert len(msite.screens) == 1
        assert msite.z_offset == [0.0]
        assert msite.r_offset == [0.0]
        assert msite.paralax == [0.0]

    def test_msite_get_names(self, sample_insert):
        """Test MSite get_names method"""
        msite = MSite("names_msite", [sample_insert], None, None, None, None)
        
        names = msite.get_names("test_prefix")
        assert isinstance(names, list)
        assert len(names) > 0


