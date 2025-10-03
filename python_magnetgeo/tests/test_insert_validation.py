import pytest
from python_magnetgeo.ModelAxi import ModelAxi
from python_magnetgeo.Model3D import Model3D
from python_magnetgeo.Shape import Shape
from python_magnetgeo.Helix import Helix
from python_magnetgeo.Ring import Ring
from python_magnetgeo.Insert import Insert
from python_magnetgeo.validation import ValidationError

def test_insert_valid_no_rings():
    """Test Insert with helices but no rings is valid"""
    
    # Create nested objects
    modelaxi = ModelAxi(
        name="test_helix",
        h=0.048,
        turns=[5, 7],
        pitch=[0.008, 0.008]
    )
    
    h1 = Helix("H1", [10, 20], [0, 50], 0.2, True, False, modelaxi=modelaxi)
    h2 = Helix("H2", [25, 35], [0, 50], 0.2, True, False, modelaxi=modelaxi)
    
    # Should succeed - rings are optional
    insert = Insert(
        name="test",
        helices=[h1, h2],
        rings=[],
        currentleads=[],
        hangles=[],
        rangles=[],
        innerbore=5.0,
        outerbore=60.0
    )
    assert len(insert.helices) == 2
    assert len(insert.rings) == 0

def test_insert_valid_with_rings():
    """Test Insert with correct helix/ring ratio"""
    # Create nested objects
    modelaxi = ModelAxi(
        name="test_helix",
        h=0.048,
        turns=[5, 7],
        pitch=[0.008, 0.008]
    )
    
    h1 = Helix("H1", [10, 20], [0, 50], 0.2, True, False, modelaxi=modelaxi)
    h2 = Helix("H2", [25, 35], [0, 50], 0.2, True, False, modelaxi=modelaxi)
    h3 = Helix("H3", [40, 50], [0, 50], 0.2, True, False, modelaxi=modelaxi)
    
    r1 = Ring("R1", [10, 20, 25, 35], [50, 55])  # connects H1 and H2
    r2 = Ring("R2", [25, 35, 40, 50], [50, 55])  # connects H2 and H3
    
    # 3 helices need 2 connecting rings - should succeed
    insert = Insert(
        name="test",
        helices=[h1, h2, h3],
        rings=[r1, r2],
        currentleads=[],
        hangles=[],
        rangles=[],
        innerbore=5.0,
        outerbore=60.0
    )
    assert len(insert.helices) == 3
    assert len(insert.rings) == 2

def test_insert_invalid_ring_count():
    """Test Insert rejects wrong number of rings"""
    # Create nested objects
    modelaxi = ModelAxi(
        name="test_helix",
        h=0.048,
        turns=[5, 7],
        pitch=[0.008, 0.008]
    )
    
    h1 = Helix("H1", [10, 20], [0, 50], 0.2, True, False, modelaxi=modelaxi)
    h2 = Helix("H2", [25, 35], [0, 50], 0.2, True, False, modelaxi=modelaxi)
    
    r1 = Ring("R1", [20, 22, 25, 27], [50, 55])
    r2 = Ring("R2", [35, 37, 40, 42], [50, 55])
    
    # 2 helices need 1 ring, but providing 2 - should fail
    with pytest.raises(ValidationError, match="must be equal to number of helices"):
        Insert(
            name="test",
            helices=[h1, h2],
            rings=[r1, r2],  # Too many rings!
            currentleads=[],
            hangles=[],
            rangles=[]
        )

def test_insert_invalid_single_helix_with_rings():
    """Test Insert rejects rings when only 1 helix"""
    # Create nested objects
    modelaxi = ModelAxi(
        name="test_helix",
        h=0.048,
        turns=[5, 7],
        pitch=[0.008, 0.008]
    )
    
    h1 = Helix("H1", [10, 20], [0, 50], 0.2, True, False, modelaxi=modelaxi)
    r1 = Ring("R1", [20, 22, 25, 27], [50, 55])
    
    # Can't connect 1 helix with ring - need at least 2
    with pytest.raises(ValidationError, match="must be equal to number of helices"):
        Insert(
            name="test",
            helices=[h1],
            rings=[r1],
            currentleads=[],
            hangles=[],
            rangles=[]
        )

def test_insert_invalid_hangles_count():
    """Test Insert rejects mismatched hangles"""
    # Create nested objects
    modelaxi = ModelAxi(
        name="test_helix",
        h=0.048,
        turns=[5, 7],
        pitch=[0.008, 0.008]
    )

    h1 = Helix("H1", [10, 20], [0, 50], 0.2, True, False, modelaxi=modelaxi)
    h2 = Helix("H2", [25, 35], [0, 50], 0.2, True, False, modelaxi=modelaxi)
    
    with pytest.raises(ValidationError, match="Number of hangles.*must match"):
        Insert(
            name="test",
            helices=[h1, h2],
            rings=[],
            currentleads=[],
            hangles=[90.0],  # 2 helices but only 1 angle!
            rangles=[]
        )

def test_insert_invalid_rangles_count():
    """Test Insert rejects mismatched rangles"""
    # Create nested objects
    modelaxi = ModelAxi(
        name="test_helix",
        h=0.048,
        turns=[5, 7],
        pitch=[0.008, 0.008]
    )
    
    h1 = Helix("H1", [10, 20], [0, 50], 0.2, True, False, modelaxi=modelaxi)
    h2 = Helix("H2", [25, 35], [0, 50], 0.2, True, False, modelaxi=modelaxi)
    r1 = Ring("R1", [20, 22, 25, 27], [50, 55])
    
    with pytest.raises(ValidationError, match="Number of rangles.*must match"):
        Insert(
            name="test",
            helices=[h1, h2],
            rings=[r1],
            currentleads=[],
            hangles=[],
            rangles=[90.0, 180.0]  # 1 ring but 2 angles!
        )