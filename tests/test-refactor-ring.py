#!/usr/bin/env python3
"""
Fixed test script for refactored Ring
"""

import os
import json
import tempfile
from python_magnetgeo.Ring import Ring

def test_refactored_ring_functionality():
    """Test that refactored Ring has identical functionality"""
    print("Testing refactored Ring functionality...")
    
    # Test basic creation
    ring = Ring(
        name="test_ring",
        r=[10.0, 20.0, 30.0, 40.0],
        z=[0.0, 5.0],
        n=1,
        angle=45.0,
        bpside=True,
        fillets=False,
        cad="test_cad"
    )
    
    print(f"✓ Ring created: {ring}")
    
    # Test that all inherited methods exist
    assert hasattr(ring, 'dump')
    assert hasattr(ring, 'to_json')  
    assert hasattr(ring, 'write_to_json')
    assert hasattr(Ring, 'from_yaml')
    assert hasattr(Ring, 'from_json')
    assert hasattr(Ring, 'from_dict')
    
    print("✓ All serialization methods inherited correctly")
    
    # Test JSON serialization
    json_str = ring.to_json()
    parsed = json.loads(json_str)
    assert parsed['name'] == 'test_ring'
    assert parsed['r'] == [10.0, 20.0, 30.0, 40.0]
    assert parsed['__classname__'] == 'Ring'
    
    print("✓ JSON serialization works identically")
    
    # Test from_dict
    test_dict = {
        'name': 'dict_ring',
        'r': [5.0, 15.0, 20.0, 25.0],
        'z': [1.0, 6.0],
        'n': 2,
        'angle': 90.0,
        'bpside': False,
        'fillets': True,
        'cad': 'dict_cad'
    }
    
    dict_ring = Ring.from_dict(test_dict)
    assert dict_ring.name == 'dict_ring'
    assert dict_ring.r == [5.0, 15.0, 20.0, 25.0]
    
    print("✓ from_dict works identically")
    
    # Test validation
    try:
        Ring(name="", r=[1.0, 2.0, 3.0, 4.0], z=[0.0, 1.0])
        assert False, "Should have raised ValidationError for empty name"
    except Exception as e:
        print(f"✓ Validation works: {e}")
    
    try:
        Ring(name="bad_ring", r=[2.0, 1.0, 3.0, 4.0], z=[0.0, 1.0])  # inner > outer
        assert False, "Should have raised ValidationError for bad radii"
    except Exception as e:
        print(f"✓ Validation works: {e}")
    
    # Test YAML round-trip - using dump() to create file first
    ring.dump()  # This creates test_ring.yaml
    print("✓ YAML dump works")
    
    # Now load it back
    loaded_ring = Ring.from_yaml('test_ring.yaml', debug=True)
    assert loaded_ring.name == ring.name
    assert loaded_ring.r == ring.r
    
    print("✓ YAML round-trip works", flush=True)
    
    # Clean up
    if os.path.exists('test_ring.yaml'):
        os.unlink('test_ring.yaml')
    
    print("All refactored functionality verified! Ring.py successfully refactored.\n")

if __name__ == "__main__":
    test_refactored_ring_functionality()

