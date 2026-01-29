#!/usr/bin/env python3
"""
Test utilities and runner script for python_magnetgeo v0.7.0 test suite
Provides common testing utilities and a comprehensive test runner
"""

# File: new-tests/test_utils.py
import json
import yaml
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union
from unittest.mock import Mock
import pytest


class TestDataFactory:
    """Factory for creating consistent test data across test modules"""

    @staticmethod
    def create_modelaxi_data(name: str = "test_axi") -> Dict[str, Any]:
        """Create ModelAxi test data"""
        return {
            "name": name,
            "h": 25.0,
            "turns": [2.5, 3.0, 2.8],
            "pitch": [8.0, 9.0, 8.5]
        }

    @staticmethod
    def create_shape_data(name: str = "test_shape") -> Dict[str, Any]:
        """Create Shape test data"""
        return {
            "name": name,
            "profile": "rectangular",
            "length": 10,
            "angle": [90.0, 90.0, 90.0, 90.0],
            "onturns": 0,
            "position": "BELOW"
        }

    @staticmethod
    def create_helix_data(name: str = "test_helix") -> Dict[str, Any]:
        """Create Helix test data"""
        return {
            "name": name,
            "r": [15.0, 25.0],
            "z": [0.0, 100.0],
            "cutwidth": 2.0,
            "odd": True,
            "dble": False
        }

    @staticmethod
    def create_ring_data(name: str = "test_ring") -> Dict[str, Any]:
        """Create Ring test data"""
        return {
            "name": name,
            "r": [12.0, 12.1, 27.9, 28.0],
            "z": [45.0, 55.0]
        }

    @staticmethod
    def create_supra_data(name: str = "test_supra") -> Dict[str, Any]:
        """Create Supra test data"""
        return {
            "name": name,
            "r": [20.0, 40.0],
            "z": [10.0, 90.0],
            "n": 5,
            "struct": "LTS"
        }

    @staticmethod
    def create_probe_data(name: str = "test_probe") -> Dict[str, Any]:
        """Create Probe test data"""
        return {
            "name": name,
            "type": "voltage_taps",
            "index": ["V1", "V2", "V3"],
            "locations": [
                [16.0, 0.0, 25.0],
                [20.0, 0.0, 50.0],
                [24.0, 0.0, 75.0]
            ]
        }

    @staticmethod
    def create_insert_data(name: str = "test_insert") -> Dict[str, Any]:
        """Create Insert test data"""
        return {
            "name": name,
            "helices": ["helix1"],
            "rings": ["ring1"],
            "currentleads": ["inner_lead"],
            "hangles": [180.0],
            "rangles": [90.0],
            "innerbore": 10.0,
            "outerbore": 30.0,
            "probes": []
        }

    @staticmethod
    def create_screen_data(name: str = "test_screen") -> Dict[str, Any]:
        """Create Screen test data"""
        return {
            "name": name,
            "r": [5.0, 50.0],
            "z": [0.0, 100.0]
        }


class GeometricAssertions:
    """Assertions for geometric operations"""

    @staticmethod
    def assert_valid_bounding_box(rb: List[float], zb: List[float]) -> None:
        """Assert bounding box has valid format and values"""
        assert isinstance(rb, list), "r bounds must be a list"
        assert isinstance(zb, list), "z bounds must be a list"
        assert len(rb) == 2, "r bounds must have exactly 2 elements"
        assert len(zb) == 2, "z bounds must have exactly 2 elements"
        assert rb[0] <= rb[1], "r_min must be <= r_max"
        assert zb[0] <= zb[1], "z_min must be <= z_max"
        assert all(isinstance(x, (int, float)) for x in rb), "r bounds must be numeric"
        assert all(isinstance(x, (int, float)) for x in zb), "z bounds must be numeric"

    @staticmethod
    def assert_bounding_box_contains(outer_rb: List[float], outer_zb: List[float],
                                   inner_rb: List[float], inner_zb: List[float]) -> None:
        """Assert outer bounding box contains inner bounding box"""
        assert outer_rb[0] <= inner_rb[0], "Outer r_min must be <= inner r_min"
        assert outer_rb[1] >= inner_rb[1], "Outer r_max must be >= inner r_max"
        assert outer_zb[0] <= inner_zb[0], "Outer z_min must be <= inner z_min"
        assert outer_zb[1] >= inner_zb[1], "Outer z_max must be >= inner z_max"

    @staticmethod
    def assert_valid_intersection_result(result: Any) -> None:
        """Assert intersection result is a boolean"""
        assert isinstance(result, bool), "Intersection result must be boolean"

    @staticmethod
    def assert_rectangles_overlap(r1: List[float], z1: List[float],
                                r2: List[float], z2: List[float]) -> bool:
        """Calculate if two rectangles should overlap"""
        r_overlap = r1[0] < r2[1] and r2[0] < r1[1]
        z_overlap = z1[0] < z2[1] and z2[0] < z1[1]
        return r_overlap and z_overlap


class SerializationAssertions:
    """Assertions for serialization operations"""

    @staticmethod
    def assert_valid_json_structure(json_str: str, expected_classname: str) -> Dict[str, Any]:
        """Assert JSON string has valid structure and return parsed data"""
        assert isinstance(json_str, str), "JSON output must be string"

        try:
            parsed = json.loads(json_str)
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON structure: {e}")

        assert isinstance(parsed, dict), "JSON must deserialize to dict"
        assert "__classname__" in parsed, "JSON must contain __classname__ field"
        assert parsed["__classname__"] == expected_classname, f"Expected classname {expected_classname}"
        assert "name" in parsed, "JSON must contain name field"

        return parsed

    @staticmethod
    def assert_serialization_preserves_data(original_obj: Any, json_str: str) -> None:
        """Assert serialization preserves essential object data"""
        parsed = json.loads(json_str)

        # Check name preservation
        assert parsed["name"] == original_obj.name

        # Check geometric data if present
        if hasattr(original_obj, 'r'):
            assert parsed["r"] == original_obj.r
        if hasattr(original_obj, 'z'):
            assert parsed["z"] == original_obj.z

    @staticmethod
    def assert_has_serialization_interface(cls: Type) -> None:
        """Assert class implements required serialization methods"""
        required_class_methods = ['from_dict', 'from_yaml', 'from_json']
        required_instance_methods = ['to_json', 'write_to_json', 'write_to_yaml']

        for method_name in required_class_methods:
            assert hasattr(cls, method_name), f"Class missing method: {method_name}"
            assert callable(getattr(cls, method_name)), f"Method {method_name} not callable"

        # Test with a simple instance
        if hasattr(cls, '__init__'):
            try:
                # Create minimal instance for testing
                if cls.__name__ == 'Screen':
                    instance = cls("test", [1.0, 2.0], [0.0, 1.0])
                elif cls.__name__ == 'Ring':
                    instance = cls("test", [1.0, 2.0], [0.0, 1.0])
                elif cls.__name__ == 'Supra':
                    instance = cls("test", [1.0, 2.0], [0.0, 1.0], 1, "test")
                elif cls.__name__ == 'Probe':
                    instance = cls("test", "voltage", ["V1"], [[1.0, 0.0, 0.0]])
                else:
                    return  # Skip instance method testing for complex classes

                for method_name in required_instance_methods:
                    assert hasattr(instance, method_name), f"Instance missing method: {method_name}"
                    assert callable(getattr(instance, method_name)), f"Method {method_name} not callable"

            except Exception:
                # If we can't create instance, skip instance method testing
                pass


class YAMLTestUtils:
    """Utilities for YAML testing"""

    @staticmethod
    def create_temp_yaml_file(content: str) -> str:
        """Create temporary YAML file with content"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(content)
            return f.name

    @staticmethod
    def create_yaml_content(obj_type: str, data: Dict[str, Any]) -> str:
        """Create YAML content with proper type annotation"""
        yaml_dict = {f'!<{obj_type}>': data}
        return yaml.dump(yaml_dict, default_flow_style=False)

    @staticmethod
    def assert_yaml_tag_exists(cls: Type, expected_tag: str) -> None:
        """Assert class has correct YAML tag"""
        assert hasattr(cls, 'yaml_tag'), f"Class {cls.__name__} missing yaml_tag"
        assert cls.yaml_tag == expected_tag, f"Expected tag {expected_tag}, got {cls.yaml_tag}"


class ProbeTestUtils:
    """Utilities for testing probe functionality"""

    @staticmethod
    def create_sample_probes() -> List[Dict[str, Any]]:
        """Create various types of sample probes for testing"""
        return [
            {
                "name": "voltage_probes",
                "type": "voltage_taps",
                "index": ["V1", "V2", "V3"],
                "locations": [[10.0, 0.0, 5.0], [15.0, 0.0, 10.0], [20.0, 0.0, 15.0]]
            },
            {
                "name": "temp_probes",
                "type": "temperature",
                "index": [1, 2, 3, 4],
                "locations": [[12.0, 2.0, 8.0], [16.0, -2.0, 12.0], [18.0, 0.0, 16.0], [22.0, 1.0, 20.0]]
            },
            {
                "name": "hall_probes",
                "type": "hall_sensors",
                "index": ["H1", "H2"],
                "locations": [[14.0, 5.0, 25.0], [19.0, -5.0, 35.0]]
            }
        ]

    @staticmethod
    def assert_valid_probe_data(probe_obj: Any) -> None:
        """Assert probe object has valid data structure"""
        assert hasattr(probe_obj, 'name'), "Probe missing name attribute"
        assert hasattr(probe_obj, 'type'), "Probe missing type attribute"
        assert hasattr(probe_obj, 'index'), "Probe missing index attribute"
        assert hasattr(probe_obj, 'locations'), "Probe missing locations attribute"

        assert isinstance(probe_obj.index, list), "Probe index must be list"
        assert isinstance(probe_obj.locations, list), "Probe locations must be list"
        assert len(probe_obj.index) == len(probe_obj.locations), "Index and locations must have same length"

        for location in probe_obj.locations:
            assert isinstance(location, list), "Each location must be a list"
            assert len(location) == 3, "Each location must have exactly 3 coordinates [x, y, z]"
            assert all(isinstance(coord, (int, float)) for coord in location), "Coordinates must be numeric"

    @staticmethod
    def assert_probe_integration(magnet_obj: Any, expected_probe_count: int) -> None:
        """Assert magnet object properly integrates probes"""
        assert hasattr(magnet_obj, 'probes'), "Magnet object missing probes attribute"
        assert isinstance(magnet_obj.probes, list), "Probes must be a list"
        assert len(magnet_obj.probes) == expected_probe_count, f"Expected {expected_probe_count} probes"


class SuiteRunner:
    """Comprehensive test runner with reporting and validation"""

    def __init__(self, test_dir: str = "new-tests"):
        self.test_dir = Path(test_dir)
        self.results = {}

    def validate_test_environment(self) -> bool:
        """Validate test environment is properly set up"""
        try:
            # Check python_magnetgeo can be imported
            import python_magnetgeo
            print("✓ python_magnetgeo import successful")

            # Check required test dependencies
            import pytest
            import yaml
            print("✓ Test dependencies available")

            # Check test directory exists
            if not self.test_dir.exists():
                print(f"✗ Test directory {self.test_dir} does not exist")
                return False
            print(f"✓ Test directory {self.test_dir} found")

            # Check test files exist
            expected_files = [
                "conftest.py",
                "test_core_classes.py",
                "test_serialization.py",
                "test_geometric_operations.py",
                "test_probe_integration.py",
                "test_magnet_collections.py",
                "test_yaml_constructors.py",
                "test_integration.py"
            ]

            missing_files = []
            for file in expected_files:
                if not (self.test_dir / file).exists():
                    missing_files.append(file)

            if missing_files:
                print(f"✗ Missing test files: {missing_files}")
                return False
            print("✓ All test files present")

            return True

        except ImportError as e:
            print(f"✗ Import error: {e}")
            return False
        except Exception as e:
            print(f"✗ Environment validation error: {e}")
            return False

    def run_smoke_tests(self) -> bool:
        """Run quick smoke tests to verify basic functionality"""
        print("\n=== Running Smoke Tests ===")

        try:
            # Test basic class imports
            from python_magnetgeo.Insert import Insert
            from python_magnetgeo.Helix import Helix
            from python_magnetgeo.Ring import Ring
            from python_magnetgeo.Supra import Supra
            from python_magnetgeo.Screen import Screen
            from python_magnetgeo.Probe import Probe
            print("✓ Core class imports successful")

            # Test basic object creation
            screen = Screen("smoke_screen", [1.0, 2.0], [0.0, 1.0])
            assert screen.name == "smoke_screen"
            print("✓ Basic object creation works")

            # Test serialization
            json_str = screen.to_json()
            assert '"name": "smoke_screen"' in json_str
            print("✓ Basic serialization works")

            # Test geometric operations
            rb, zb = screen.boundingBox()
            assert rb == [1.0, 2.0]
            assert zb == [0.0, 1.0]
            print("✓ Basic geometric operations work")

            return True

        except Exception as e:
            print(f"✗ Smoke test failed: {e}")
            return False

    def run_test_suite(self, test_pattern: str = None, verbose: bool = True) -> Dict[str, Any]:
        """Run the complete test suite"""
        import subprocess
        import sys

        print("\n=== Running Full Test Suite ===")

        # Build pytest command
        cmd = [sys.executable, "-m", "pytest", str(self.test_dir)]

        if verbose:
            cmd.append("-v")

        if test_pattern:
            cmd.extend(["-k", test_pattern])

        # Add coverage if available
        try:
            import pytest_cov
            cmd.extend(["--cov=python_magnetgeo", "--cov-report=term-missing"])
        except ImportError:
            pass

        # Run tests
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            self.results = {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }

            print(f"Test suite completed with return code: {result.returncode}")

            if verbose:
                print("\n--- Test Output ---")
                print(result.stdout)
                if result.stderr:
                    print("\n--- Errors ---")
                    print(result.stderr)

            return self.results

        except subprocess.TimeoutExpired:
            print("✗ Test suite timed out after 5 minutes")
            return {"success": False, "error": "timeout"}
        except Exception as e:
            print(f"✗ Error running test suite: {e}")
            return {"success": False, "error": str(e)}

    def run_specific_tests(self, test_categories: List[str]) -> Dict[str, Any]:
        """Run specific test categories"""
        results = {}

        for category in test_categories:
            print(f"\n=== Running {category} Tests ===")
            test_file = f"test_{category}.py"
            result = self.run_test_suite(test_pattern=test_file)
            results[category] = result

        return results

    def generate_report(self) -> str:
        """Generate a comprehensive test report"""
        if not self.results:
            return "No test results available. Run tests first."

        report = []
        report.append("# Python MagnetGeo v0.7.0 Test Report")
        report.append(f"Generated: {__import__('datetime').datetime.now()}")
        report.append("")

        if self.results["success"]:
            report.append("## ✓ Test Suite PASSED")
        else:
            report.append("## ✗ Test Suite FAILED")

        report.append(f"Return Code: {self.results['returncode']}")
        report.append("")

        # Parse test output for summary statistics
        output = self.results.get("stdout", "")
        if "passed" in output or "failed" in output:
            report.append("## Test Summary")
            # Extract summary line from pytest output
            lines = output.split('\n')
            for line in lines:
                if " passed" in line or " failed" in line or " error" in line:
                    report.append(f"```\n{line}\n```")
                    break
            report.append("")

        if self.results.get("stderr"):
            report.append("## Errors")
            report.append(f"```\n{self.results['stderr']}\n```")
            report.append("")

        # Add recommendations
        report.append("## Recommendations")
        if self.results["success"]:
            report.append("- All tests passing - API implementation is ready")
            report.append("- Consider running with coverage analysis")
            report.append("- Review any deprecation warnings in output")
        else:
            report.append("- Review failed tests and fix implementation issues")
            report.append("- Check for missing method implementations")
            report.append("- Verify YAML constructor registration")
            report.append("- Validate probe integration completeness")

        return "\n".join(report)


# File: new-tests/run_tests.py
#!/usr/bin/env python3
"""
Test runner script for python_magnetgeo v0.7.0
Provides comprehensive testing with validation and reporting
"""

import argparse
import sys
from pathlib import Path
from test_utils import SuiteRunner


def main():
    parser = argparse.ArgumentParser(
        description="Test runner for python_magnetgeo v0.7.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                          # Run all tests
  python run_tests.py --smoke-only             # Quick smoke tests only
  python run_tests.py --category core          # Run core class tests only
  python run_tests.py --pattern test_helix     # Run tests matching pattern
  python run_tests.py --no-validate            # Skip environment validation
  python run_tests.py --quiet                  # Minimal output
        """
    )

    parser.add_argument(
        '--test-dir',
        default='new-tests',
        help='Test directory path (default: new-tests)'
    )

    parser.add_argument(
        '--smoke-only',
        action='store_true',
        help='Run only smoke tests for quick validation'
    )

    parser.add_argument(
        '--category',
        choices=['core', 'serialization', 'geometric', 'probe', 'collections', 'yaml', 'integration'],
        help='Run specific test category only'
    )

    parser.add_argument(
        '--pattern',
        help='Run tests matching pytest pattern (e.g., test_helix)'
    )

    parser.add_argument(
        '--no-validate',
        action='store_true',
        help='Skip environment validation'
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Minimal output'
    )

    parser.add_argument(
        '--report',
        help='Generate report file at specified path'
    )

    args = parser.parse_args()

    # Initialize test runner
    runner = SuiteRunner(args.test_dir)

    # Environment validation
    if not args.no_validate:
        print("=== Environment Validation ===")
        if not runner.validate_test_environment():
            print("Environment validation failed. Use --no-validate to skip.")
            sys.exit(1)

    # Smoke tests
    if args.smoke_only:
        success = runner.run_smoke_tests()
        sys.exit(0 if success else 1)

    if not args.no_validate:
        smoke_success = runner.run_smoke_tests()
        if not smoke_success:
            print("Smoke tests failed. Continuing with full suite...")

    # Run tests based on arguments
    if args.category:
        results = runner.run_specific_tests([args.category])
        success = all(r.get("success", False) for r in results.values())
    else:
        result = runner.run_test_suite(
            test_pattern=args.pattern,
            verbose=not args.quiet
        )
        success = result.get("success", False)

    # Generate report if requested
    if args.report:
        report = runner.generate_report()
        with open(args.report, 'w') as f:
            f.write(report)
        print(f"\nReport generated: {args.report}")

    # Print summary
    if not args.quiet:
        print("\n" + "="*50)
        if success:
            print("✓ TEST SUITE PASSED")
            print("python_magnetgeo v0.7.0 API implementation validated")
        else:
            print("✗ TEST SUITE FAILED")
            print("Review failed tests and fix implementation issues")
        print("="*50)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()


# File: new-tests/validate_implementation.py
#!/usr/bin/env python3
"""
Implementation validation script for python_magnetgeo v0.7.0
Checks that all expected methods and classes are properly implemented
"""

import inspect
import sys
from typing import Dict, List, Any, Optional


class ImplementationValidator:
    """Validates that the current implementation matches v0.7.0 expectations"""

    def __init__(self):
        self.validation_results = {}
        self.missing_implementations = []
        self.unexpected_implementations = []

    def validate_class_exists(self, module_name: str, class_name: str) -> bool:
        """Validate that a class exists and can be imported"""
        try:
            module = __import__(f"python_magnetgeo.{module_name}", fromlist=[class_name])
            cls = getattr(module, class_name)
            return inspect.isclass(cls)
        except (ImportError, AttributeError):
            return False

    def validate_method_exists(self, module_name: str, class_name: str, method_name: str) -> bool:
        """Validate that a method exists on a class"""
        try:
            module = __import__(f"python_magnetgeo.{module_name}", fromlist=[class_name])
            cls = getattr(module, class_name)
            return hasattr(cls, method_name) and callable(getattr(cls, method_name))
        except (ImportError, AttributeError):
            return False

    def validate_yaml_constructor(self, module_name: str, class_name: str) -> bool:
        """Validate that YAML constructor is properly registered"""
        try:
            module = __import__(f"python_magnetgeo.{module_name}", fromlist=[f"{class_name}_constructor"])
            constructor = getattr(module, f"{class_name}_constructor")
            return callable(constructor)
        except (ImportError, AttributeError):
            return False

    def validate_core_classes(self) -> Dict[str, bool]:
        """Validate core geometry classes"""
        core_classes = {
            "Helix": ["boundingBox", "intersect", "get_type", "insulators", "to_json", "from_dict"],
            "Ring": ["boundingBox", "to_json", "from_dict"],
            "Supra": ["boundingBox", "intersect", "get_lc", "set_Detail", "get_Nturns", "to_json", "from_dict"],
            "Screen": ["boundingBox", "intersect", "get_lc", "get_names", "to_json", "from_dict"],
            "Probe": ["get_probe_count", "get_probe_by_index", "add_probe", "to_json", "from_dict"]
        }

        results = {}
        for class_name, methods in core_classes.items():
            class_exists = self.validate_class_exists(class_name, class_name)
            results[class_name] = {
                "class_exists": class_exists,
                "methods": {}
            }

            if class_exists:
                for method in methods:
                    method_exists = self.validate_method_exists(class_name, class_name, method)
                    results[class_name]["methods"][method] = method_exists
                    if not method_exists:
                        self.missing_implementations.append(f"{class_name}.{method}")

        return results

    def validate_collection_classes(self) -> Dict[str, bool]:
        """Validate magnet collection classes"""
        collection_classes = {
            "Insert": ["boundingBox", "intersect", "get_nhelices", "get_channels", "to_json", "from_dict"],
            "Supras": ["boundingBox", "to_json", "from_dict"],
            "Bitters": ["boundingBox", "to_json", "from_dict"],
            "MSite": ["boundingBox", "get_names", "get_channels", "to_json", "from_dict"]
        }

        results = {}
        for class_name, methods in collection_classes.items():
            module_name = class_name  # Module name matches class name
            class_exists = self.validate_class_exists(module_name, class_name)
            results[class_name] = {
                "class_exists": class_exists,
                "methods": {}
            }

            if class_exists:
                for method in methods:
                    method_exists = self.validate_method_exists(module_name, class_name, method)
                    results[class_name]["methods"][method] = method_exists
                    if not method_exists:
                        self.missing_implementations.append(f"{class_name}.{method}")

        return results

    def validate_yaml_system(self) -> Dict[str, bool]:
        """Validate YAML constructor system"""
        yaml_classes = ["Insert", "Helix", "Ring", "Supra", "Supras", "Bitters", "Screen", "MSite", "Probe"]

        results = {}
        for class_name in yaml_classes:
            # Check yaml_tag attribute
            has_yaml_tag = False
            try:
                module = __import__(f"python_magnetgeo.{class_name}", fromlist=[class_name])
                cls = getattr(module, class_name)
                has_yaml_tag = hasattr(cls, 'yaml_tag') and cls.yaml_tag == class_name
            except (ImportError, AttributeError):
                pass

            # Check constructor function
            has_constructor = self.validate_yaml_constructor(class_name, class_name)

            results[class_name] = {
                "yaml_tag": has_yaml_tag,
                "constructor": has_constructor
            }

            if not has_yaml_tag:
                self.missing_implementations.append(f"{class_name}.yaml_tag")
            if not has_constructor:
                self.missing_implementations.append(f"{class_name}_constructor")

        return results

    def validate_serialization_interface(self) -> Dict[str, bool]:
        """Validate serialization interface consistency"""
        classes_to_check = ["Insert", "Helix", "Ring", "Supra", "Supras", "Screen", "MSite", "Probe"]
        required_methods = {
            "class_methods": ["from_dict", "from_yaml", "from_json"],
            "instance_methods": ["to_json", "write_to_json", "write_to_yaml"]
        }

        results = {}
        for class_name in classes_to_check:
            try:
                module = __import__(f"python_magnetgeo.{class_name}", fromlist=[class_name])
                cls = getattr(module, class_name)

                class_method_results = {}
                for method in required_methods["class_methods"]:
                    has_method = hasattr(cls, method) and callable(getattr(cls, method))
                    class_method_results[method] = has_method
                    if not has_method:
                        self.missing_implementations.append(f"{class_name}.{method} (class method)")

                # For instance methods, we'll check if they exist as attributes
                instance_method_results = {}
                for method in required_methods["instance_methods"]:
                    # Check if method exists in class definition
                    has_method = method in cls.__dict__ or any(method in base.__dict__ for base in cls.__mro__)
                    instance_method_results[method] = has_method
                    if not has_method:
                        self.missing_implementations.append(f"{class_name}.{method} (instance method)")

                results[class_name] = {
                    "class_methods": class_method_results,
                    "instance_methods": instance_method_results
                }

            except (ImportError, AttributeError):
                results[class_name] = {"error": "Class not found"}

        return results

    def run_full_validation(self) -> Dict[str, Any]:
        """Run complete implementation validation"""
        print("=== Python MagnetGeo v0.7.0 Implementation Validation ===\n")

        # Validate core classes
        print("Validating core classes...")
        core_results = self.validate_core_classes()

        # Validate collection classes
        print("Validating collection classes...")
        collection_results = self.validate_collection_classes()

        # Validate YAML system
        print("Validating YAML system...")
        yaml_results = self.validate_yaml_system()

        # Validate serialization interface
        print("Validating serialization interface...")
        serialization_results = self.validate_serialization_interface()

        return {
            "core_classes": core_results,
            "collection_classes": collection_results,
            "yaml_system": yaml_results,
            "serialization": serialization_results,
            "missing_implementations": self.missing_implementations,
            "summary": self.generate_summary()
        }

    def generate_summary(self) -> Dict[str, Any]:
        """Generate validation summary"""
        total_missing = len(self.missing_implementations)

        return {
            "total_missing_implementations": total_missing,
            "validation_passed": total_missing == 0,
            "critical_issues": [impl for impl in self.missing_implementations if "boundingBox" in impl or "to_json" in impl],
            "recommendations": self.get_recommendations()
        }

    def get_recommendations(self) -> List[str]:
        """Get recommendations based on validation results"""
        recommendations = []

        if len(self.missing_implementations) == 0:
            recommendations.append("✓ All expected implementations found")
            recommendations.append("✓ Ready to run full test suite")
        else:
            recommendations.append("✗ Missing implementations detected")
            recommendations.append("✗ Implement missing methods before running tests")

            # Priority recommendations
            critical_missing = [impl for impl in self.missing_implementations
                              if any(critical in impl for critical in ["boundingBox", "to_json", "from_dict"])]
            if critical_missing:
                recommendations.append("Priority: Implement critical methods first:")
                recommendations.extend(f"  - {impl}" for impl in critical_missing[:5])

        return recommendations

    def print_validation_report(self, results: Dict[str, Any]) -> None:
        """Print detailed validation report"""
        print("\n" + "="*60)
        print("VALIDATION REPORT")
        print("="*60)

        # Summary
        summary = results["summary"]
        if summary["validation_passed"]:
            print("✓ VALIDATION PASSED")
        else:
            print("✗ VALIDATION FAILED")
            print(f"Missing implementations: {summary['total_missing_implementations']}")

        print()

        # Recommendations
        print("RECOMMENDATIONS:")
        for rec in summary["recommendations"]:
            print(f"  {rec}")

        # Missing implementations details
        if results["missing_implementations"]:
            print(f"\nMISSING IMPLEMENTATIONS ({len(results['missing_implementations'])}):")
            for impl in results["missing_implementations"][:10]:  # Show first 10
                print(f"  - {impl}")
            if len(results["missing_implementations"]) > 10:
                print(f"  ... and {len(results['missing_implementations']) - 10} more")

        print("\n" + "="*60)


def main():
    validator = ImplementationValidator()
    results = validator.run_full_validation()
    validator.print_validation_report(results)

    # Exit with appropriate code
    sys.exit(0 if results["summary"]["validation_passed"] else 1)


if __name__ == "__main__":
    main()
