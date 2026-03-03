import pytest
import json
import yaml
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import Mock

import sys
import os
# Add the parent directory to Python path so we can import from python_magnetgeo
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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


@pytest.fixture(scope="session", autouse=True)
def change_test_dir():
    """Change to tests.yaml directory for all tests to find yaml fixtures"""
    original_dir = os.getcwd()
    test_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(test_dir)
    yield
    os.chdir(original_dir)


@pytest.fixture
def sample_modelaxi():
    """Fixture providing a sample ModelAxi object"""
    return ModelAxi(
        name="test_axi",
        h=35.4,
        turns=[2.5, 3.0, 2.8],
        pitch=[8.0, 9.0, 8.5]
    )


@pytest.fixture
def sample_model3d():
    """Fixture providing a sample Model3D object"""
    return Model3D(
        name="test_model3d",
        cad="test_cad",
        with_shapes=False,
        with_channels=False
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
        position="BELOW"
    )


@pytest.fixture
def sample_helix(sample_modelaxi, sample_model3d, sample_shape):
    """Fixture providing a sample Helix object"""
    return Helix(
        name="test_helix",
        r=[15.0, 25.0],
        z=[0.0, 100.0],
        cutwidth=2.0,
        odd=True,
        dble=False,
        modelaxi=sample_modelaxi,
        model3d=sample_model3d,
        shape=sample_shape
    )


@pytest.fixture
def sample_ring():
    """Fixture providing a sample Ring object"""
    return Ring(
        name="test_ring",
        r=[12.0, 12.1, 27.9, 28.0],
        z=[45.0, 55.0],
        n=6,
        angle=30.0,
        bpside=True,
        fillets=False
    )


@pytest.fixture
def sample_probe():
    """Fixture providing a sample Probe object"""
    return Probe(
        name="test_probe",
        type="voltage_taps",
        labels=["V1", "V2", "V3"],
        points=[[16.0, 0.0, 25.0], [20.0, 0.0, 50.0], [24.0, 0.0, 75.0]]
    )


@pytest.fixture
def sample_insert(sample_helix, sample_ring, sample_probe):
    """Fixture providing a sample Insert object"""
    return Insert(
        name="test_insert",
        helices=[sample_helix],
        rings=[],
        currentleads=["inner_lead"],
        hangles=[180.0],
        rangles=[],
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
        struct=None  # Empty struct to avoid file loading
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