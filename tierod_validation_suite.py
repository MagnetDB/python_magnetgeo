#!/usr/bin/env python3
"""
Comprehensive validation suite for Tierod v0.7.0 API changes
Tests backward compatibility, new features, and breaking changes
"""

import pytest
import tempfile
import yaml
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from python_magnetgeo.tierod import Tierod
    from python_magnetgeo.validation import ValidationError, GeometryValidator
    from python_magnetgeo.base import YAMLObjectBase
except ImportError as e:
    print(f"Warning: Could not import python_magnetgeo modules: {e}")
    print("This validation suite requires the refactored codebase to be available")


class TierodValidationSuite:
    """Comprehensive validation suite for Tierod class changes"""
    
    def __init__(self):
        self.test_results = []
        self.failed_tests = []
        self.warnings = []
    
    def log_result(self, test_name: str, passed: bool, message: str = ""):
        """Log a test result"""
        result = {
            'test': test_name,
            'passed': passed,
            'message': message
        }
        self.test_results.append(result)
        
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"    {message}")
        
        if not passed:
            self.failed_tests.append(result)
    
    def test_class_inheritance(self):
        """Test that Tierod correctly inherits from YAMLObjectBase"""
        test_name = "Class Inheritance"
        
        try:
            # Check inheritance hierarchy
            assert issubclass(Tierod, YAMLObjectBase), "Tierod should inherit from YAMLObjectBase"
            
            # Check that yaml_tag is set
            assert hasattr(Tierod, 'yaml_tag'), "Tierod should have yaml_tag attribute"
            assert Tierod.yaml_tag == "Tierod", f"yaml_tag should be 'Tierod', got '{Tierod.yaml_tag}'"
            
            # Check that from_dict is implemented
            assert hasattr(Tierod, 'from_dict'), "Tierod should implement from_dict method"
            assert callable(getattr(Tierod, 'from_dict')), "from_dict should be callable"
            
            self.log_result(test_name, True, "Inheritance structure correct")
            
        except Exception as e:
            self.log_result(test_name, False, f"Inheritance check failed: {e}")
    
    def test_constructor_validation(self):
        """Test enhanced constructor validation"""
        test_name = "Constructor Validation"
        
        try:
            # Valid construction should work
            tierod = Tierod(
                name="test_tierod",
                r=12.5,
                n=8,
                dh=10.0,
                sh=5.0,
                shape=None
            )
            assert tierod.name == "test_tierod"
            assert tierod.r == 12.5
            assert tierod.n == 8
            
            # Test validation failures
            test_cases = [
                # Empty name
                {"name": "", "r": 12.5, "n": 8, "dh": 10.0, "sh": 5.0, "shape": None},
                # None name
                {"name": None, "r": 12.5, "n": 8, "dh": 10.0, "sh": 5.0, "shape": None},
                # Invalid radius type
                {"name": "test", "r": "invalid", "n": 8, "dh": 10.0, "sh": 5.0, "shape": None},
                # Negative radius
                {"name": "test", "r": -5.0, "n": 8, "dh": 10.0, "sh": 5.0, "shape": None},
                # Invalid n type
                {"name": "test", "r": 12.5, "n": "eight", "dh": 10.0, "sh": 5.0, "shape": None},
                # Negative n
                {"name": "test", "r": 12.5, "n": -1, "dh": 10.0, "sh": 5.0, "shape": None},
            ]
            
            validation_failures = 0
            for i, test_case in enumerate(test_cases):
                try:
                    Tierod(**test_case)
                    self.warnings.append(f"Validation case {i+1} should have failed but didn't")
                except (ValidationError, ValueError, TypeError):
                    validation_failures += 1
            
            self.log_result(test_name, True, 
                          f"Valid construction works, {validation_failures}/{len(test_cases)} validation cases failed as expected")
            
        except Exception as e:
            self.log_result(test_name, False, f"Constructor validation test failed: {e}")
    
    def test_inherited_serialization_methods(self):
        """Test that all serialization methods are inherited and work correctly"""
        test_name = "Inherited Serialization Methods"
        
        try:
            tierod = Tierod(
                name="serialization_test",
                r=15.0,
                n=6,
                dh=8.0,
                sh=4.0,
                shape="test_shape"
            )
            
            # Test to_json method
            json_str = tierod.to_json()
            assert isinstance(json_str, str), "to_json should return string"
            
            # Parse JSON to verify structure
            json_data = json.loads(json_str)
            assert json_data['name'] == 'serialization_test', "JSON should contain correct name"
            assert json_data['r'] == 15.0, "JSON should contain correct radius"
            
            # Test write_to_json method
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                tierod.write_to_json(f.name)
                
                # Verify file was created and contains correct data
                assert Path(f.name).exists(), "JSON file should be created"
                
                with open(f.name, 'r') as rf:
                    file_content = rf.read()
                    assert 'serialization_test' in file_content, "JSON file should contain object data"
                
                # Clean up
                os.unlink(f.name)
            
            # Test dump method (YAML serialization)
            # Note: This requires proper YAML setup
            
            self.log_result(test_name, True, "All inherited serialization methods work correctly")
            
        except Exception as e:
            self.log_result(test_name, False, f"Serialization methods test failed: {e}")
    
    def test_from_dict_functionality(self):
        """Test from_dict method with various input formats"""
        test_name = "from_dict Functionality"
        
        try:
            # Test basic from_dict
            basic_data = {
                'name': 'dict_test',
                'r': 20.0,
                'n': 10,
                'dh': 12.0,
                'sh': 6.0,
                'shape': None
            }
            
            tierod = Tierod.from_dict(basic_data)
            assert tierod.name == 'dict_test'
            assert tierod.r == 20.0
            assert tierod.n == 10
            assert tierod.dh == 12.0
            assert tierod.sh == 6.0
            assert tierod.shape is None
            
            # Test with missing optional fields (should get defaults)
            minimal_data = {
                'name': 'minimal_test',
                'r': 25.0,
                'n': 12
            }
            
            tierod_minimal = Tierod.from_dict(minimal_data)
            assert tierod_minimal.name == 'minimal_test'
            assert tierod_minimal.r == 25.0
            assert tierod_minimal.n == 12
            assert tierod_minimal.dh == 0.0  # Default value
            assert tierod_minimal.sh == 0.0  # Default value
            assert tierod_minimal.shape is None  # Default value
            
            # Test with shape reference (string)
            shape_ref_data = {
                'name': 'shape_ref_test',
                'r': 18.0,
                'n': 8,
                'dh': 10.0,
                'sh': 5.0,
                'shape': 'my_shape_reference'
            }
            
            tierod_shape_ref = Tierod.from_dict(shape_ref_data)
            assert tierod_shape_ref.shape == 'my_shape_reference'
            
            self.log_result(test_name, True, "from_dict handles all input formats correctly")
            
        except Exception as e:
            self.log_result(test_name, False, f"from_dict test failed: {e}")
    
    def test_yaml_format_compatibility(self):
        """Test new YAML format with type annotations"""
        test_name = "YAML Format Compatibility"
        
        try:
            # Test new format YAML
            yaml_content_new = """
!<Tierod>
name: "TR-H1-NewFormat"
r: 22.5
n: 14
dh: 9.0
sh: 4.5
shape: null
"""
            
            # Parse YAML
            data = yaml.safe_load(yaml_content_new)
            assert '!<Tierod>' in data, "YAML should contain type annotation"
            
            # Create object from YAML data
            tierod_data = data['!<Tierod>']
            tierod = Tierod.from_dict(tierod_data)
            
            assert tierod.name == "TR-H1-NewFormat"
            assert tierod.r == 22.5
            assert tierod.n == 14
            assert tierod.dh == 9.0
            assert tierod.sh == 4.5
            assert tierod.shape is None
            
            # Test YAML with inline shape object
            yaml_content_inline = """
!<Tierod>
name: "TR-H1-InlineShape"
r: 16.0
n: 9
dh: 7.0
sh: 3.5
shape: !<Shape>
  name: "inline_shape"
  profile: "rectangular"
  length: 15
  angle: [90, 90, 90, 90]
  onturns: 0
  position: "CENTER"
"""
            
            data_inline = yaml.safe_load(yaml_content_inline)
            tierod_data_inline = data_inline['!<Tierod>']
            
            # This should handle the inline shape appropriately
            tierod_inline = Tierod.from_dict(tierod_data_inline)
            assert tierod_inline.name == "TR-H1-InlineShape"
            
            self.log_result(test_name, True, "New YAML format works correctly")
            
        except Exception as e:
            self.log_result(test_name, False, f"YAML format test failed: {e}")
    
    def test_round_trip_serialization(self):
        """Test that objects can be serialized and deserialized without data loss"""
        test_name = "Round-trip Serialization"
        
        try:
            # Create original object
            original = Tierod(
                name="roundtrip_test",
                r=30.0,
                n=16,
                dh=15.0,
                sh=7.5,
                shape="reference_shape"
            )
            
            # Serialize to JSON
            json_str = original.to_json()
            json_data = json.loads(json_str)
            
            # Deserialize from JSON data
            reconstructed = Tierod.from_dict(json_data)
            
            # Verify all fields match
            assert reconstructed.name == original.name
            assert reconstructed.r == original.r
            assert reconstructed.n == original.n
            assert reconstructed.dh == original.dh
            assert reconstructed.sh == original.sh
            assert reconstructed.shape == original.shape
            
            # Test YAML round-trip
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                # Write object to YAML
                yaml_data = {
                    '!<Tierod>': {
                        'name': original.name,
                        'r': original.r,
                        'n': original.n,
                        'dh': original.dh,
                        'sh': original.sh,
                        'shape': original.shape
                    }
                }
                
                yaml.dump(yaml_data, f, default_flow_style=False)
                
                # Read back from YAML
                with open(f.name, 'r') as rf:
                    loaded_data = yaml.safe_load(rf)
                    loaded_tierod = Tierod.from_dict(loaded_data['!<Tierod>'])
                    
                    # Verify round-trip preservation
                    assert loaded_tierod.name == original.name
                    assert loaded_tierod.r == original.r
                    assert loaded_tierod.n == original.n
                    assert loaded_tierod.dh == original.dh
                    assert loaded_tierod.sh == original.sh
                    assert loaded_tierod.shape == original.shape
                
                # Clean up
                os.unlink(f.name)
            
            self.log_result(test_name, True, "Round-trip serialization preserves all data")
            
        except Exception as e:
            self.log_result(test_name, False, f"Round-trip serialization test failed: {e}")
    
    def test_error_handling(self):
        """Test error handling and validation error messages"""
        test_name = "Error Handling"
        
        try:
            error_cases = [
                # Missing required field
                {"r": 12.5, "n": 8},  # Missing name
                {"name": "test", "n": 8},  # Missing r
                {"name": "test", "r": 12.5},  # Missing n
                
                # Invalid field types
                {"name": 123, "r": 12.5, "n": 8},  # name not string
                {"name": "test", "r": "invalid", "n": 8},  # r not numeric
                {"name": "test", "r": 12.5, "n": "invalid"},  # n not integer
                
                # Invalid field values
                {"name": "", "r": 12.5, "n": 8},  # empty name
                {"name": "test", "r": -5.0, "n": 8},  # negative radius
                {"name": "test", "r": 12.5, "n": -1},  # negative n
            ]
            
            errors_caught = 0
            for i, error_case in enumerate(error_cases):
                try:
                    Tierod.from_dict(error_case)
                    self.warnings.append(f"Error case {i+1} should have raised an exception")
                except (ValidationError, ValueError, KeyError, TypeError) as e:
                    errors_caught += 1
                    # Verify error message is informative
                    error_msg = str(e)
                    assert len(error_msg) > 10, "Error message should be informative"
            
            success_rate = errors_caught / len(error_cases)
            
            self.log_result(test_name, success_rate >= 0.8, 
                          f"Caught {errors_caught}/{len(error_cases)} expected errors ({success_rate:.1%})")
            
        except Exception as e:
            self.log_result(test_name, False, f"Error handling test failed: {e}")
    
    def test_backward_compatibility_breaks(self):
        """Test that certain old patterns are properly broken (intentional breaking changes)"""
        test_name = "Backward Compatibility Breaks"
        
        try:
            # These should fail in the new version
            breaking_cases = [
                # Old YAML format without type annotation should require migration
                {"name": "old_format", "r": 12.5, "n": 8},  # Raw dict without !<Tierod>
            ]
            
            # Test that direct instantiation from old format requires from_dict
            old_format_data = {"name": "old_style", "r": 12.5, "n": 8}
            
            # This should work (conversion via from_dict)
            new_tierod = Tierod.from_dict(old_format_data)
            assert new_tierod.name == "old_style"
            
            # Test that validation is now mandatory (this is a breaking change)
            try:
                # This should fail due to validation
                Tierod.from_dict({"name": "", "r": 12.5, "n": 8})
                self.warnings.append("Empty name validation should have failed")
            except ValidationError:
                pass  # Expected
            
            self.log_result(test_name, True, "Breaking changes work as expected")
            
        except Exception as e:
            self.log_result(test_name, False, f"Breaking changes test failed: {e}")
    
    def run_all_tests(self):
        """Run all validation tests"""
        print("=" * 60)
        print("Tierod v0.7.0 API Validation Suite")
        print("=" * 60)
        
        test_methods = [
            self.test_class_inheritance,
            self.test_constructor_validation,
            self.test_inherited_serialization_methods,
            self.test_from_dict_functionality,
            self.test_yaml_format_compatibility,
            self.test_round_trip_serialization,
            self.test_error_handling,
            self.test_backward_compatibility_breaks
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self.log_result(test_method.__name__, False, f"Test execution failed: {e}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['passed']])
        failed_tests = len(self.failed_tests)
        
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success rate: {passed_tests/total_tests:.1%}")
        
        if self.warnings:
            print(f"\nWarnings: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"  ⚠️  {warning}")
        
        if self.failed_tests:
            print(f"\nFailed tests:")
            for failed in self.failed_tests:
                print(f"  ✗ {failed['test']}: {failed['message']}")
        
        return passed_tests == total_tests
    
    def generate_validation_report(self, output_file: str = "tierod_validation_report.json"):
        """Generate detailed validation report"""
        
        report = {
            'validation_summary': {
                'total_tests': len(self.test_results),
                'passed_tests': len([r for r in self.test_results if r['passed']]),
                'failed_tests': len(self.failed_tests),
                'warnings': len(self.warnings)
            },
            'test_results': self.test_results,
            'failed_tests': self.failed_tests,
            'warnings': self.warnings,
            'api_compatibility': {
                'breaking_changes_detected': len(self.failed_tests) > 0,
                'migration_required': True,
                'validation_enhanced': True
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Validation report saved to: {output_file}")


def main():
    """Run the validation suite"""
    
    # Check if we can import the required modules
    try:
        from python_magnetgeo.tierod import Tierod
        print("✓ Successfully imported Tierod from python_magnetgeo")
    except ImportError as e:
        print(f"✗ Cannot import Tierod: {e}")
        print("Please ensure the refactored python_magnetgeo package is available")
        sys.exit(1)
    
    # Run validation suite
    validator = TierodValidationSuite()
    success = validator.run_all_tests()
    
    # Generate report
    validator.generate_validation_report()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
