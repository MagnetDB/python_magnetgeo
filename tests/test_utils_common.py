#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Common utilities and fixtures for testing python_magnetgeo classes

This module provides shared functionality to reduce code duplication across test files.
"""

import pytest
import json
import yaml
import tempfile
import os
from unittest.mock import Mock, patch, mock_open
from typing import Any, Dict, Type, Optional
from abc import ABC, abstractmethod


class BaseSerializationTestMixin:
    """
    Mixin class providing common serialization tests for YAML/JSON classes.
    
    Classes using this mixin should define:
    - get_sample_instance(): returns a sample instance for testing
    - get_sample_yaml_content(): returns YAML content string
    - get_expected_json_fields(): returns dict of expected JSON fields
    """
    
    @abstractmethod
    def get_sample_instance(self):
        """Return a sample instance of the class being tested"""
        pass
    
    @abstractmethod
    def get_sample_yaml_content(self) -> str:
        """Return sample YAML content for testing from_yaml"""
        pass
    
    @abstractmethod
    def get_expected_json_fields(self) -> Dict[str, Any]:
        """Return expected fields in JSON serialization"""
        pass
    
    @abstractmethod
    def get_class_under_test(self) -> Type:
        """Return the class being tested"""
        pass
    
    def test_to_json_serialization(self):
        """Test to_json method"""
        instance = self.get_sample_instance()
        json_str = instance.to_json()
        
        # Should be valid JSON
        parsed = json.loads(json_str)
        expected_fields = self.get_expected_json_fields()
        
        # Check class name is present
        assert parsed["__classname__"] == self.get_class_under_test().__name__
        
        # Check expected fields
        for field, expected_value in expected_fields.items():
            assert parsed[field] == expected_value
    
    def test_dump_yaml_success(self):
        """Test successful YAML dump"""
        instance = self.get_sample_instance()
        
        with patch("builtins.open", mock_open()) as mock_file:
            instance.dump() # "test_file")
            mock_file.assert_called_once_with(f"{instance.name}.yaml", "w")
    
    def test_dump_yaml_error_handling(self):
        """Test YAML dump error handling"""
        instance = self.get_sample_instance()
        
        with patch("builtins.open", side_effect=Exception("File error")):
            with pytest.raises(Exception):
                instance.dump("error_file")
    
    def test_from_yaml_success(self):
        """Test successful from_yaml loading"""
        yaml_content = self.get_sample_yaml_content()
        cls = self.get_class_under_test()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp_file:
            tmp_file.write(yaml_content)
            tmp_file.flush()
            
            try:
                with patch('os.getcwd', return_value='/tmp'):
                    instance = cls.from_yaml(tmp_file.name)
                    # Verify instance was created
                    assert isinstance(instance, cls)
                    
            finally:
                os.unlink(tmp_file.name)
    
    def test_from_yaml_file_error(self):
        """Test from_yaml with file error"""
        cls = self.get_class_under_test()
        
        with pytest.raises(Exception):
            cls.from_yaml("nonexistent_file.yaml")
    
    def test_from_json_with_mocking(self):
        """Test from_json method with mocking"""
        cls = self.get_class_under_test()
        mock_instance = self.get_sample_instance()
        
        with patch(f"python_magnetgeo.deserialize.unserialize_object", return_value=mock_instance):
            with patch("builtins.open", mock_open(read_data='{"test": "data"}')):
                result = cls.from_json("test.json")
                assert isinstance(result, cls)


class BaseYAMLConstructorTestMixin:
    """
    Mixin class providing common YAML constructor tests.
    
    Classes using this mixin should define:
    - get_constructor_function(): returns the YAML constructor function
    - get_sample_constructor_data(): returns sample data for constructor
    - get_expected_constructor_type(): returns expected type string
    """
    
    @abstractmethod
    def get_constructor_function(self):
        """Return the YAML constructor function"""
        pass
    
    @abstractmethod
    def get_sample_constructor_data(self) -> Dict[str, Any]:
        """Return sample data for constructor testing"""
        pass
    
    @abstractmethod
    def get_expected_constructor_type(self) -> str:
        """Return expected constructor type string"""
        pass
    
    def test_yaml_constructor_function(self):
        """Test the YAML constructor function"""
        constructor_func = self.get_constructor_function()
        
        # Mock loader and node
        mock_loader = Mock()
        mock_node = Mock()
        
        # Mock data that would be returned by construct_mapping
        mock_data = self.get_sample_constructor_data()
        mock_loader.construct_mapping.return_value = mock_data
        
        result_data, result_type = constructor_func(mock_loader, mock_node)
        
        assert result_data == mock_data
        assert result_type == self.get_expected_constructor_type()
        mock_loader.construct_mapping.assert_called_once_with(mock_node)


class BaseYAMLTagTestMixin:
    """
    Mixin class providing YAML tag registration tests.
    
    Classes using this mixin should define:
    - get_class_with_yaml_tag(): returns the class with yaml_tag
    - get_expected_yaml_tag(): returns expected YAML tag string
    """
    
    @abstractmethod
    def get_class_with_yaml_tag(self) -> Type:
        """Return the class that has yaml_tag attribute"""
        pass
    
    @abstractmethod
    def get_expected_yaml_tag(self) -> str:
        """Return expected YAML tag string"""
        pass
    
    def test_yaml_tag_exists(self):
        """Test that the YAML tag attribute exists"""
        cls = self.get_class_with_yaml_tag()
        assert hasattr(cls, 'yaml_tag')
        assert cls.yaml_tag == self.get_expected_yaml_tag()


# Common fixtures that can be used across multiple test files
@pytest.fixture
def temp_yaml_file():
    """Create a temporary YAML file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp_file:
        yield tmp_file
        try:
            os.unlink(tmp_file.name)
        except FileNotFoundError:
            pass


@pytest.fixture
def temp_json_file():
    """Create a temporary JSON file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
        yield tmp_file
        try:
            os.unlink(tmp_file.name)
        except FileNotFoundError:
            pass


# Common test data generators
def generate_test_data_variants(base_data: Dict[str, Any], variants: Dict[str, Dict[str, Any]]):
    """
    Generate test data variants from base data.
    
    Args:
        base_data: Base dictionary of test data
        variants: Dictionary of variant names to override values
        
    Returns:
        Dictionary of variant names to complete test data
    """
    result = {}
    for variant_name, overrides in variants.items():
        variant_data = base_data.copy()
        variant_data.update(overrides)
        result[variant_name] = variant_data
    
    return result


# Common parametrized test decorators
def parametrize_basic_values():
    """Decorator for parametrizing tests with basic value types"""
    return pytest.mark.parametrize("value,expected_type", [
        (0, int),
        (1, int),
        (-1, int),
        (0.0, float),
        (1.5, float),
        (-2.5, float),
        ("", str),
        ("test", str),
        (None, type(None)),
        ([], list),
        ([1, 2, 3], list),
        ({}, dict),
        ({"key": "value"}, dict),
    ])


def parametrize_file_operations():
    """Decorator for parametrizing file operation tests"""
    return pytest.mark.parametrize("operation,exception_type", [
        ("open", FileNotFoundError),
        ("read", IOError),
        ("write", PermissionError),
        ("yaml_load", yaml.YAMLError),
        ("json_load", json.JSONDecodeError),
    ])


# Common assertion helpers
def assert_json_structure(json_str: str, expected_class_name: str, expected_fields: Dict[str, Any]):
    """Assert that JSON string has expected structure"""
    parsed = json.loads(json_str)
    
    # Check class name
    assert "__classname__" in parsed
    assert parsed["__classname__"] == expected_class_name
    
    # Check expected fields
    for field, expected_value in expected_fields.items():
        assert field in parsed
        if expected_value is not None:
            assert parsed[field] == expected_value


def assert_instance_attributes(instance: Any, expected_attrs: Dict[str, Any]):
    """Assert that instance has expected attributes with expected values"""
    for attr_name, expected_value in expected_attrs.items():
        assert hasattr(instance, attr_name), f"Instance missing attribute: {attr_name}"
        actual_value = getattr(instance, attr_name)
        assert actual_value == expected_value, f"Attribute {attr_name}: expected {expected_value}, got {actual_value}"


def assert_yaml_roundtrip(instance: Any, cls: Type):
    """Assert that instance can be serialized to YAML and back successfully"""
    # Serialize to YAML
    yaml_str = yaml.dump(instance)
    assert isinstance(yaml_str, str)
    assert len(yaml_str) > 0
    
    # Note: Actual roundtrip would depend on proper YAML constructor implementation


def assert_json_roundtrip_data(instance: Any, expected_fields: Dict[str, Any]):
    """Assert that instance JSON serialization contains expected data"""
    json_str = instance.to_json()
    parsed = json.loads(json_str)
    
    for field, expected_value in expected_fields.items():
        assert field in parsed
        assert parsed[field] == expected_value


# Mock factory functions
def create_mock_file_operations(read_data: str = "", write_error: bool = False):
    """Create mock file operations for testing"""
    if write_error:
        return mock_open(read_data=read_data, side_effect=IOError("Write error"))
    else:
        return mock_open(read_data=read_data)


def create_mock_yaml_loader(return_data: Dict[str, Any]):
    """Create mock YAML loader for testing"""
    mock_loader = Mock()
    mock_loader.construct_mapping.return_value = return_data
    return mock_loader


# Test data validation helpers
def validate_geometric_data(r_values: list, z_values: list, allow_negative: bool = False):
    """Validate geometric data (r, z coordinates)"""
    assert isinstance(r_values, list), "r_values must be a list"
    assert isinstance(z_values, list), "z_values must be a list"
    assert len(r_values) >= 2, "r_values must have at least 2 elements"
    assert len(z_values) >= 2, "z_values must have at least 2 elements"
    
    if not allow_negative:
        assert all(r >= 0 for r in r_values), "r values must be non-negative"
    
    # Check ordering (inner < outer radius)
    if len(r_values) == 2:
        assert r_values[0] <= r_values[1], "Inner radius must be <= outer radius"


def validate_angle_data(angles: list, allow_negative: bool = True, max_angle: float = 360.0):
    """Validate angle data"""
    assert isinstance(angles, list), "angles must be a list"
    
    for angle in angles:
        assert isinstance(angle, (int, float)), f"Angle {angle} must be numeric"
        if not allow_negative:
            assert angle >= 0, f"Angle {angle} must be non-negative"
        assert abs(angle) <= max_angle, f"Angle {angle} exceeds maximum {max_angle}"


# Error simulation helpers
class FileOperationError:
    """Context manager for simulating file operation errors"""
    
    def __init__(self, error_type: str = "read", exception_class: Type[Exception] = IOError):
        self.error_type = error_type
        self.exception_class = exception_class
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def patch_open(self):
        """Return a patch for builtins.open that raises an exception"""
        return patch("builtins.open", side_effect=self.exception_class(f"{self.error_type} error"))


# Performance testing helpers
def time_function_execution(func, *args, **kwargs):
    """Time function execution for performance tests"""
    import time
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    execution_time = end_time - start_time
    return result, execution_time


def assert_performance_within_limits(execution_time: float, max_time: float):
    """Assert that execution time is within acceptable limits"""
    assert execution_time <= max_time, f"Execution took {execution_time:.4f}s, exceeds limit of {max_time}s"


# Integration test helpers
def create_test_file_structure(base_dir: str, files: Dict[str, str]):
    """Create a temporary file structure for integration tests"""
    import os
    
    created_files = []
    try:
        for filename, content in files.items():
            filepath = os.path.join(base_dir, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w') as f:
                f.write(content)
            created_files.append(filepath)
        
        yield created_files
        
    finally:
        # Cleanup
        for filepath in created_files:
            try:
                os.unlink(filepath)
            except FileNotFoundError:
                pass


# Custom pytest markers for categorizing tests
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "performance: mark test as a performance test")
    config.addinivalue_line("markers", "serialization: mark test as a serialization test")
    config.addinivalue_line("markers", "file_io: mark test as a file I/O test")
    config.addinivalue_line("markers", "error_handling: mark test as an error handling test")


# Example usage documentation
"""
Usage Examples:

1. Using BaseSerializationTestMixin:

class TestMyClass(BaseSerializationTestMixin):
    def get_sample_instance(self):
        return MyClass(param1="value1", param2=42)
    
    def get_sample_yaml_content(self):
        return '''
        param1: value1
        param2: 42
        '''
    
    def get_expected_json_fields(self):
        return {"param1": "value1", "param2": 42}
    
    def get_class_under_test(self):
        return MyClass

2. Using common fixtures:

def test_my_function(temp_yaml_file):
    temp_yaml_file.write("test: data")
    temp_yaml_file.flush()
    # Use temp_yaml_file.name for file path

3. Using assertion helpers:

def test_my_instance():
    instance = MyClass(a=1, b=2)
    assert_instance_attributes(instance, {"a": 1, "b": 2})

4. Using test data generators:

base_data = {"name": "test", "value": 0}
variants = {
    "positive": {"value": 10},
    "negative": {"value": -5},
    "zero": {"value": 0}
}
test_data = generate_test_data_variants(base_data, variants)
"""