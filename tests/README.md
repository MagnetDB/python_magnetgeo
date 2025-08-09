# Python MagnetGeo Test Suite v0.7.0

This test suite is designed for the current API (v0.7.0) and tests only implemented methods.

## Test Categories

### Core Classes (`test_core_classes.py`)
- **Helix**: Magnet coil geometry and operations
- **Ring**: Ring magnet components  
- **Supra**: Superconducting magnet elements
- **Screen**: Geometric screen components
- **Probe**: Measurement probe system

### Serialization (`test_serialization.py`)
- JSON serialization/deserialization
- YAML loading via from_yaml/from_dict
- Data integrity preservation
- Roundtrip serialization testing

### Geometric Operations (`test_geometric_operations.py`)
- Bounding box calculations
- Intersection detection
- Characteristic length computation
- Coordinate system consistency

### Probe Integration (`test_probe_integration.py`)
- Probe collections in magnet classes
- Probe lookup and management
- Integration with Insert/Supras/MSite
- String reference handling

### Magnet Collections (`test_magnet_collections.py`)
- **Insert**: Multi-helix magnet assemblies
- **Supras**: Superconducting magnet collections
- **MSite**: Complete magnet site definitions
- Collection-level operations

### YAML Constructors (`test_yaml_constructors.py`)
- YAML tag registration
- Constructor function validation
- Loading mechanism testing

### Integration (`test_integration.py`)
- End-to-end workflows
- Complex object creation
- Multi-class interactions
- Error handling validation

## Running Tests

### Run All Tests
```bash
cd new-tests
python -m pytest