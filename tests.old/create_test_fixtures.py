#!/usr/bin/env python3
"""
Create missing YAML test fixtures for tests.old directory
Run this script from the tests.old directory to create all required YAML files.

Usage:
    cd tests.old
    python create_test_fixtures.py
"""

import os
from pathlib import Path

def create_yaml_fixtures():
    """Create all missing YAML test fixtures"""
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    
    # Define all YAML fixtures needed by tests
    fixtures = {
        "inner_lead.yaml": """!<InnerCurrentLead>
name: "inner_lead"
r: [10.0, 12.0]
h: 60.0
holes: []
support: []
fillet: false
""",
        
        "lead1.yaml": """!<InnerCurrentLead>
name: "lead1"
r: [11.0, 13.0]
h: 65.0
holes: []
support: []
fillet: false
""",
        
        "inner.yaml": """!<InnerCurrentLead>
name: "inner"
r: [9.0, 11.0]
h: 55.0
holes: []
support: []
fillet: false
""",
        
        "helix1.yaml": """!<Helix>
name: "helix1"
r: [15.0, 25.0]
z: [0.0, 50.0]
cutwidth: 1.5
odd: true
dble: false
""",
        
        "ring1.yaml": """!<Ring>
name: "ring1"
r: [20.0, 30.0]
z: [10.0, 20.0]
n: 1
angle: 0.0
bpside: true
fillets: false
""",
        
        # Additional fixtures for comprehensive testing
        "test_helix.yaml": """!<Helix>
name: "test_helix"
r: [12.0, 22.0]
z: [0.0, 60.0]
cutwidth: 1.8
odd: false
dble: true
""",
        
        "test_ring.yaml": """!<Ring>
name: "test_ring"
r: [10.0, 20.0]
z: [25.0, 35.0]
n: 6
angle: 30.0
bpside: true
fillets: false
""",
        
        "test_insert.yaml": """!<Insert>
name: "test_insert"
helices:
  - test_helix
rings:
  - test_ring
currentleads:
  - inner_lead
hangles: [0.0]
rangles: []
innerbore: 8.0
outerbore: 26.0
probes: []
""",
        
        # Probe fixture
        "test_probe.yaml": """!<Probe>
name: "test_probe"
type: "voltage_taps"
channels: ["V1", "V2", "V3"]
positions:
  - [15.0, 0.0, 10.0]
  - [15.0, 0.0, 30.0]
  - [15.0, 0.0, 50.0]
""",
        
        # ModelAxi fixture
        "test_modelaxi.yaml": """!<ModelAxi>
name: "test_axi"
h: 86.51
turns: [3.0, 2.5, 2.0]
pitch: [10.0, 12.0, 15.0]
""",
        
        # Shape fixture
        "test_shape.yaml": """!<Shape>
name: "test_shape"
profile: "rectangular"
length: 8
angle: [90.0, 90.0, 90.0, 90.0]
onturns: 0
position: "BELOW"
""",
    }
    
    print("=" * 70)
    print("Creating YAML Test Fixtures for tests.old")
    print("=" * 70)
    print()
    
    created_count = 0
    skipped_count = 0
    
    for filename, content in fixtures.items():
        filepath = script_dir / filename
        
        if filepath.exists():
            print(f"⊘ Skipped (already exists): {filename}")
            skipped_count += 1
        else:
            with open(filepath, 'w') as f:
                f.write(content.strip() + '\n')
            print(f"✓ Created: {filename}")
            created_count += 1
    
    print()
    print("=" * 70)
    print(f"Summary:")
    print(f"  Created: {created_count} files")
    print(f"  Skipped: {skipped_count} files (already existed)")
    print(f"  Total:   {len(fixtures)} fixtures")
    print("=" * 70)
    print()
    
    if created_count > 0:
        print("✓ Test fixtures created successfully!")
        print()
        print("Next steps:")
        print("  1. Run tests: python -m pytest -v")
        print("  2. Check specific test: python -m pytest test_integration.py -v")
        print()
    else:
        print("ℹ All fixtures already exist. No changes made.")
        print()

def verify_fixtures():
    """Verify that all created fixtures are valid YAML"""
    import yaml
    
    script_dir = Path(__file__).parent
    yaml_files = list(script_dir.glob("*.yaml"))
    
    if not yaml_files:
        print("⚠ No YAML files found to verify")
        return
    
    print("=" * 70)
    print("Verifying YAML Fixtures")
    print("=" * 70)
    print()
    
    valid_count = 0
    invalid_count = 0
    
    for filepath in sorted(yaml_files):
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Check for type annotation
            if not content.strip().startswith('!<'):
                print(f"⚠ {filepath.name}: Missing type annotation")
                invalid_count += 1
                continue
            
            # Try to parse
            data = yaml.safe_load(content)
            
            # Check for name field
            if 'name' not in data:
                print(f"⚠ {filepath.name}: Missing 'name' field")
                invalid_count += 1
                continue
            
            print(f"✓ {filepath.name}: Valid ({data.get('name', 'unknown')})")
            valid_count += 1
            
        except Exception as e:
            print(f"✗ {filepath.name}: Parse error - {e}")
            invalid_count += 1
    
    print()
    print("=" * 70)
    print(f"Verification Summary:")
    print(f"  Valid:   {valid_count} files")
    print(f"  Invalid: {invalid_count} files")
    print("=" * 70)
    print()

def main():
    """Main entry point"""
    print()
    create_yaml_fixtures()
    
    # Ask if user wants to verify
    try:
        response = input("Would you like to verify the fixtures? (y/n): ").strip().lower()
        if response == 'y':
            print()
            verify_fixtures()
    except (KeyboardInterrupt, EOFError):
        print("\n\nOperation cancelled by user.")
        return

if __name__ == "__main__":
    main()
