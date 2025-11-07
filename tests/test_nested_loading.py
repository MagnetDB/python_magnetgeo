import pytest
from python_magnetgeo.Insert import Insert
from python_magnetgeo.Helix import Helix
from python_magnetgeo.Ring import Ring
from python_magnetgeo.Bitter import Bitter
from python_magnetgeo.ModelAxi import ModelAxi
from python_magnetgeo.coolingslit import CoolingSlit

def test_load_nested_list_from_dicts():
    """Test loading list of objects from inline dicts"""
    data = [
        {'name': 'H1', 'r': [10, 20], 'z': [0, 50], 'cutwidth': 0.2, 'odd': True, 'dble': False},
        {'name': 'H2', 'r': [25, 35], 'z': [0, 50], 'cutwidth': 0.2, 'odd': True, 'dble': False}
    ]
    
    helices = Insert._load_nested_list(data, Helix)
    
    assert len(helices) == 2
    assert all(isinstance(h, Helix) for h in helices)
    assert helices[0].name == 'H1'
    assert helices[1].name == 'H2'

def test_load_nested_single_from_dict():
    """Test loading single object from inline dict"""
    data = {'name': 'test_axi', 'h': 15.0, 'turns': [3.0], 'pitch': [10.0]}
    
    modelaxi = Bitter._load_nested_single(data, ModelAxi)
    
    assert isinstance(modelaxi, ModelAxi)
    assert modelaxi.name == 'test_axi'

def test_load_nested_list_none_handling():
    """Test that None input returns empty list"""
    result = Insert._load_nested_list(None, Helix)
    assert result == []

def test_load_nested_single_none_handling():
    """Test that None input returns None"""
    result = Bitter._load_nested_single(None, ModelAxi)
    assert result is None

def test_load_nested_list_invalid_type():
    """Test error on invalid input type"""
    with pytest.raises(TypeError, match="Expected list"):
        Insert._load_nested_list("not a list", Helix)

def test_load_nested_mixed_inputs():
    """Test loading with mix of dicts and objects"""
    h1_dict = {'name': 'H1', 'r': [10, 20], 'z': [0, 50], 'cutwidth': 0.2, 'odd': True, 'dble': False}
    h2_obj = Helix('H2', [25, 35], [0, 50], 0.2, True, False)
    
    data = [h1_dict, h2_obj]
    helices = Insert._load_nested_list(data, Helix)
    
    assert len(helices) == 2
    assert helices[0].name == 'H1'
    assert helices[1].name == 'H2'