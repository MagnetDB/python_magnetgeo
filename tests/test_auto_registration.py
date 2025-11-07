import pytest
from python_magnetgeo.base import YAMLObjectBase
from python_magnetgeo.Probe import Probe
from python_magnetgeo.Shape import Shape
from python_magnetgeo.ModelAxi import ModelAxi
from python_magnetgeo.Model3D import Model3D
from python_magnetgeo.Helix import Helix
from python_magnetgeo.Ring import Ring
from python_magnetgeo.InnerCurrentLead import InnerCurrentLead
from python_magnetgeo.OuterCurrentLead import OuterCurrentLead
from python_magnetgeo.Insert import Insert
from python_magnetgeo.Bitter import Bitter
from python_magnetgeo.Supra import Supra
from python_magnetgeo.Screen import Screen
from python_magnetgeo.MSite import MSite
from python_magnetgeo.Bitters import Bitters
from python_magnetgeo.Supras import Supras
from python_magnetgeo.Contour2D import Contour2D
from python_magnetgeo.Chamfer import Chamfer
from python_magnetgeo.Groove import Groove
from python_magnetgeo.tierod import Tierod
from python_magnetgeo.coolingslit import CoolingSlit
from python_magnetgeo import list_registered_classes, verify_class_registration


def test_classes_auto_registered():
    """Test that classes are automatically registered"""
    registry = YAMLObjectBase.get_all_classes()
    
    # Check key classes are present
    assert 'Insert' in registry
    assert 'Helix' in registry
    assert 'Ring' in registry
    assert 'Bitter' in registry
    
    # Verify they're the correct classes
    assert registry['Insert'] is Insert
    assert registry['Helix'] is Helix

def test_get_class_by_name():
    """Test retrieving classes by name"""
    Ring_class = YAMLObjectBase.get_class('Ring')
    assert Ring_class is Ring
    
    # Can create instance
    ring = Ring_class(
        name="test",
        r=[10, 20, 30, 40],
        z=[0, 10]
    )
    assert isinstance(ring, Ring)

def test_list_registered_classes():
    """Test utility function"""
    classes = list_registered_classes()
    
    assert isinstance(classes, dict)
    assert len(classes) >= 15  # Should have at least 15 classes
    assert 'Insert' in classes

def test_verify_class_registration():
    """Test verification utility"""
    # Should not raise
    assert verify_class_registration() is True

def test_unknown_class_error():
    """Test error for unknown class"""
    from python_magnetgeo.deserialize import unserialize_object
    
    with pytest.raises(ValueError, match="Unknown class 'FakeClass'"):
        unserialize_object({'__classname__': 'FakeClass'}, debug=False)

def test_custom_class_auto_registers():
    """Test that custom classes auto-register"""
    
    class MyCustomGeometry(YAMLObjectBase):
        yaml_tag = "MyCustomGeometry"
        
        def __init__(self, name):
            self.name = name
        
        @classmethod
        def from_dict(cls, values, debug=False):
            return cls(values['name'])
    
    # Should be auto-registered
    registry = YAMLObjectBase.get_all_classes()
    assert 'MyCustomGeometry' in registry
    assert registry['MyCustomGeometry'] is MyCustomGeometry