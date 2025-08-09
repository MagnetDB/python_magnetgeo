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


@pytest.fixture
def sample_modelaxi():
    """Fixture providing a sample ModelAxi object"""
    return ModelAxi(
        name="test_axi",
        h=25.0,
        turns=[2.5, 3.0, 2.8],
        pitch=[8.0, 9.0, 8.5]
    )


@pytest.fixture
def sample_shape():
    """Fixture providing a sample Shape object"""
    return Shape(
        name="test_shape",
        profile="rectangular",
        length=10,
        angle=[90.0, 90.0, 90.0, 90.0],
        onturns=0,
        position="CENTER"
    )


@pytest.fixture
def sample_helix(sample_modelaxi, sample_shape):
    """Fixture providing a sample Helix object"""
    return Helix(
        name="test_helix",
        r=[15.0, 25.0],
        z=[0.0, 100.0],
        cutwidth=2.0,
        odd=True,
        dble=False,
        modelaxi=sample_modelaxi,
        shape=sample_shape
    )


@pytest.fixture
def sample_ring():
    """Fixture providing a sample Ring object"""
    return Ring(
        name="test_ring",
        r=[12.0, 28.0],
        z=[45.0, 55.0]
    )


@pytest.fixture
def sample_probe():
    """Fixture providing a sample Probe object"""
    return Probe(
        name="test_probe",
        probe_type="voltage_taps",
        index=["V1", "V2", "V3"],
        locations=[[16.0, 0.0, 25.0], [20.0, 0.0, 50.0], [24.0, 0.0, 75.0]]
    )


@pytest.fixture
def sample_insert(sample_helix, sample_ring, sample_probe):
    """Fixture providing a sample Insert object"""
    return Insert(
        name="test_insert",
        helices=[sample_helix],
        rings=[sample_ring],
        currentleads=["inner_lead"],
        hangles=[0.0, 180.0],
        rangles=[0.0, 90.0, 180.0, 270.0],
        innerbore=10.0,
        outerbore=30.0,
        probes=[sample_probe]
    )


@pytest.fixture
def sample_supra():
    """Fixture providing a sample Supra object"""
    return Supra(
        name="test_supra",
        r=[20.0, 40.0],
        z=[10.0, 90.0],
        n=5,
        struct="LTS"
    )


@pytest.fixture
def temp_yaml_file():
    """Fixture providing a temporary YAML file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yield f.name
    Path(f.name).unlink(missing_ok=True)


@pytest.fixture
def temp_json_file():
    """Fixture providing a temporary JSON file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        yield f.name
    Path(f.name).unlink(missing_ok=True)

