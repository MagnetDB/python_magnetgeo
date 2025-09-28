import json

def test_model3d_refactor():
    """Test Model3D refactor"""
    print("Testing Model3D refactor...")
    
    from python_magnetgeo.Model3D import Model3D
    
    # Test creation
    model = Model3D(
        name="test_model",
        cad="SALOME", 
        with_shapes=True,
        with_channels=False
    )
    
    print(f"✓ Model3D created: {model}")
    
    # Test inherited methods
    json_str = model.to_json()
    parsed = json.loads(json_str)
    assert parsed['name'] == 'test_model'
    assert parsed['cad'] == 'SALOME'
    
    print("✓ Model3D JSON serialization works")
    
    # Test from_dict
    dict_data = {
        'name': 'dict_model',
        'cad': 'GMSH',
        'with_shapes': False,
        'with_channels': True
    }
    
    dict_model = Model3D.from_dict(dict_data)
    assert dict_model.name == 'dict_model'
    assert dict_model.cad == 'GMSH'
    
    print("✓ Model3D from_dict works")
    print("Model3D successfully refactored!\n")

# Add this to your main test function
if __name__ == "__main__":
    test_model3d_refactor()
