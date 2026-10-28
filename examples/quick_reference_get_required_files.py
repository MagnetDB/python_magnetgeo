"""
Quick Reference: get_required_files() - Dry-Run Dependency Analysis

BASIC USAGE
-----------
from python_magnetgeo.Helix import Helix

config = {...}  # Your configuration dictionary
files = Helix.get_required_files(config)
print(files)  # Set of .yaml files that would be loaded


VALIDATION PATTERN
------------------
import os

# 1. Analyze dependencies
required_files = Helix.get_required_files(config)

# 2. Check files exist
missing = [f for f in required_files if not os.path.exists(f)]

# 3. Handle missing files
if missing:
    raise FileNotFoundError(f"Missing: {missing}")

# 4. Safe to create object
obj = Helix.from_dict(config)


DEBUG MODE
----------
# Enable to see analysis details
files = Helix.get_required_files(config, debug=True)


WHAT IT DETECTS
---------------
String reference → File:
    "modelaxi": "my_file"  →  Will load my_file.yaml ✓

Inline dict → No file:
    "modelaxi": {"num": 10, ...}  →  No file needed ✗

Mixed:
    "chamfers": ["file1", {"inline": "data"}]
    →  Will load file1.yaml only


COMMON PATTERNS
---------------

Pattern 1: Pre-flight check
    files = MyClass.get_required_files(config)
    assert all(os.path.exists(f) for f in files)

Pattern 2: Dependency count
    files = MyClass.get_required_files(config)
    print(f"Requires {len(files)} external files")

Pattern 3: List files
    files = MyClass.get_required_files(config)
    for f in sorted(files):
        print(f"  - {f}")

Pattern 4: Validation function
    def validate_config(config, cls):
        files = cls.get_required_files(config)
        missing = [f for f in files if not os.path.exists(f)]
        return len(missing) == 0, missing


RETURNS
-------
Returns: set[str]
    - Empty set if no files needed
    - Set of file paths (with .yaml extension)
    - Paths are relative to current directory


AVAILABLE FOR
-------------
All geometry classes inheriting from YAMLObjectBase:
    - Helix
    - Ring (returns empty set - no nested objects)
    - Insert (when implemented)
    - Supra (when implemented)
    - etc.


LIMITATIONS
-----------
✗ Does NOT load or validate file contents
✗ Does NOT detect circular dependencies
✗ Does NOT analyze referenced files recursively
✓ ONLY identifies immediate file dependencies
✓ Fast - no file I/O


WHEN TO USE
-----------
✓ Before calling from_dict()
✓ In validation pipelines
✓ For dependency documentation
✓ Pre-fetching files
✓ Error prevention

✗ Not needed if creating objects directly
✗ Not needed if files already validated


EXAMPLES
--------

Example 1 - All files:
    config = {
        "name": "H1",
        "modelaxi": "m1",
        "shape": "s1",
    }
    Result: {'m1.yaml', 's1.yaml'}

Example 2 - All inline:
    config = {
        "name": "H2",
        "modelaxi": {"num": 10},
    }
    Result: set()  # Empty

Example 3 - Mixed:
    config = {
        "name": "H3",
        "modelaxi": "m3",
        "shape": {"width": 5},
    }
    Result: {'m3.yaml'}
"""
