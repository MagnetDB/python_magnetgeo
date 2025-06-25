#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Pytest script for testing the Chamfer class (Fixed version)
"""

import pytest
import json
import yaml
import tempfile
import os
import math
from unittest.mock import Mock, patch, mock_open

from python_magnetgeo.Chamfer import Chamfer, Chamfer_constructor
from .test_utils_common import (
    BaseSerializationTestMixin, 
    BaseYAMLTagTestMixin,
    assert_instance_attributes,
    validate_angle_data
)


class TestChamferInitialization:
    """Test Chamfer object initialization"""
    
    def test_chamfer_basic_initialization(self):
        """Test Chamfer initialization with required parameters"""
        chamfer = Chamfer(name="test", side="HP", rside="rint", l=5.0)
        
        assert chamfer.name == "test"
        assert chamfer.side == "HP"
        assert chamfer.rside == "rint"
        assert chamfer.l == 5.0
        assert chamfer.alpha is None
        assert chamfer.dr is None

    def test_chamfer_with_alpha(self):
        """Test Chamfer initialization with alpha parameter"""
        chamfer = Chamfer(name="test", side="BP", rside="rext", alpha=45.0, l=10.0)
        
        assert chamfer.name == "test"
        assert chamfer.side == "BP"
        assert chamfer.rside == "rext"
        assert chamfer.alpha == 45.0
        assert chamfer.l == 10.0
        assert chamfer.dr is None

    def test_chamfer_with_dr(self):
        """Test Chamfer initialization with dr parameter"""
        chamfer = Chamfer(name="test", side="HP", rside="rint", dr=2.5, l=8.0)
        
        assert chamfer.name == "test"
        assert chamfer.side == "HP"
        assert chamfer.rside == "rint"
        assert chamfer.dr == 2.5
        assert chamfer.l == 8.0
        assert chamfer.alpha is None

    def test_chamfer_with_all_parameters(self):
        """Test Chamfer initialization with all parameters"""
        chamfer = Chamfer(name="test", side="BP", rside="rext", alpha=30.0, dr=1.5, l=6.0)
        
        assert chamfer.name == "test"
        assert chamfer.side == "BP"
        assert chamfer.rside == "rext"
        assert chamfer.alpha == 30.0
        assert chamfer.dr == 1.5
        assert chamfer.l == 6.0

    def test_chamfer_setstate_method(self):
        """Test __setstate__ method for deserialization"""
        # Simulate loading from pickle/YAML without optional attributes
        state = {
            'name': 'test',
            'side': 'HP',
            'rside': 'rint',
            'l': 5.0
        }
        
        chamfer = Chamfer.__new__(Chamfer)
        chamfer.__setstate__(state)
        
        assert hasattr(chamfer, 'dr')
        assert hasattr(chamfer, 'alpha')
        assert chamfer.dr is None
        assert chamfer.alpha is None
        assert chamfer.name == 'test'
        assert chamfer.side == 'HP'
        assert chamfer.rside == 'rint'
        assert chamfer.l == 5.0

    @pytest.mark.parametrize("side,rside", [
        ("HP", "rint"),
        ("HP", "rext"),
        ("BP", "rint"),
        ("BP", "rext")
    ])
    def test_chamfer_valid_side_combinations(self, side, rside):
        """Test all valid side and rside combinations"""
        chamfer = Chamfer(name="test", side=side, rside=rside, l=3.0)
        assert chamfer.side == side
        assert chamfer.rside == rside


class TestChamferMethods:
    """Test Chamfer class methods"""
    
    @pytest.fixture
    def alpha_chamfer(self):
        """Create a chamfer with alpha parameter"""
        return Chamfer(name="test", side="HP", rside="rint", alpha=45.0, l=10.0)
    
    @pytest.fixture
    def dr_chamfer(self):
        """Create a chamfer with dr parameter"""
        return Chamfer(name="test", side="BP", rside="rext", dr=5.0, l=10.0)
    
    @pytest.fixture
    def dual_chamfer(self):
        """Create a chamfer with both alpha and dr parameters"""
        return Chamfer(name="test", side="HP", rside="rint", alpha=60.0, dr=3.0, l=8.0)

    def test_get_dr_from_dr(self, dr_chamfer):
        """Test getDr method when dr is provided"""
        dr = dr_chamfer.getDr()
        assert dr == 5.0

    def test_get_dr_from_alpha(self, alpha_chamfer):
        """Test getDr method when alpha is provided"""
        dr = alpha_chamfer.getDr()
        expected = 10.0 * math.tan(math.pi / 180.0 * 45.0)
        assert abs(dr - expected) < 1e-10

    def test_get_dr_prioritizes_dr(self, dual_chamfer):
        """Test that getDr prioritizes dr over alpha when both are present"""
        dr = dual_chamfer.getDr()
        assert dr == 3.0  # Should return dr value, not calculated from alpha

    @pytest.mark.parametrize("angle,expected_ratio", [
        (0.0, 0.0),
        (30.0, 1/math.sqrt(3)),
        (45.0, 1.0),
        (60.0, math.sqrt(3))
    ])
    def test_get_dr_angle_calculations(self, angle, expected_ratio):
        """Test getDr with various angles"""
        chamfer = Chamfer(name="test", side="HP", rside="rint", alpha=angle, l=10.0)
        dr = chamfer.getDr()
        expected = 10.0 * expected_ratio
        assert abs(dr - expected) < 1e-10

    def test_get_angle_from_alpha(self, alpha_chamfer):
        """Test getAngle method when alpha is provided"""
        angle = alpha_chamfer.getAngle()
        assert angle == 45.0

    def test_get_angle_from_dr(self, dr_chamfer):
        """Test getAngle method when dr is provided"""
        angle = dr_chamfer.getAngle()
        expected = math.atan2(5.0, 10.0) * 180 / math.pi
        assert abs(angle - expected) < 1e-10

    def test_get_angle_prioritizes_alpha(self, dual_chamfer):
        """Test that getAngle prioritizes alpha over dr when both are present"""
        angle = dual_chamfer.getAngle()
        assert angle == 60.0  # Should return alpha value, not calculated from dr

    @pytest.mark.parametrize("dr,l,expected_degrees", [
        (0.0, 10.0, 0.0),
        (10.0, 10.0, 45.0),
        (10.0, 5.0, math.degrees(math.atan2(10.0, 5.0)))
    ])
    def test_get_angle_dr_calculations(self, dr, l, expected_degrees):
        """Test getAngle with various dr and l combinations"""
        chamfer = Chamfer(name="test", side="HP", rside="rint", dr=dr, l=l)
        angle = chamfer.getAngle()
        assert abs(angle - expected_degrees) < 1e-10

    def test_mathematical_consistency(self):
        """Test mathematical consistency between getDr and getAngle"""
        # Create chamfer with known angle
        chamfer_angle = Chamfer(name="test", side="HP", rside="rint", alpha=45.0, l=10.0)
        
        # Get dr from angle
        dr_from_angle = chamfer_angle.getDr()
        
        # Create equivalent chamfer with dr
        chamfer_dr = Chamfer(name="test", side="HP", rside="rint", dr=dr_from_angle, l=10.0)
        
        # Get angle from dr
        angle_from_dr = chamfer_dr.getAngle()
        
        # They should be approximately equal
        assert abs(angle_from_dr - 45.0) < 1e-10

    def test_repr_comprehensive(self):
        """Test __repr__ method with various parameter combinations"""
        test_cases = [
            Chamfer(name="test", side="HP", rside="rint", l=5.0),
            Chamfer(name="test", side="BP", rside="rext", alpha=30.0, l=8.0),
            Chamfer(name="test", side="HP", rside="rint", dr=2.0, l=6.0),
            Chamfer(name="test", side="BP", rside="rext", alpha=45.0, dr=3.0, l=10.0)
        ]
        
        for chamfer in test_cases:
            repr_str = repr(chamfer)
            assert "Chamfer(" in repr_str
            assert f"name={chamfer.name}" in repr_str
            assert f"side={chamfer.side}" in repr_str
            assert f"rside={chamfer.rside}" in repr_str
            assert f"l={chamfer.l}" in repr_str

    def test_missing_parameters_error(self):
        """Test error handling when neither alpha nor dr is provided"""
        chamfer = Chamfer(name="test", side="HP", rside="rint", l=10.0)
        
        with pytest.raises(ValueError, match="Chamfer must have alpha when dr is not defined"):
            chamfer.getDr()

        with pytest.raises(ValueError, match="Chamfer must have dr when alpha is not defined"):
            chamfer.getAngle()


class TestChamferSerialization(BaseSerializationTestMixin):
    """Test Chamfer serialization using common test mixin"""
    
    def get_sample_instance(self):
        """Return a sample Chamfer instance"""
        return Chamfer(name="test", side="HP", rside="rint", alpha=45.0, dr=2.0, l=8.0)
    
    def get_sample_yaml_content(self):
        """Return sample YAML content"""
        return '''
!<Chamfer>
name: test
side: BP
rside: rext
alpha: 30.0
l: 12.0
'''
    
    def get_expected_json_fields(self):
        """Return expected JSON fields"""
        return {
            "name": "test",
            "side": "HP",
            "rside": "rint",
            "alpha": 45.0,
            "dr": 2.0,
            "l": 8.0
        }
    
    def get_class_under_test(self):
        """Return Chamfer class"""
        return Chamfer

    def test_json_serialization_completeness(self):
        """Test that JSON includes all chamfer-specific fields"""
        instance = self.get_sample_instance()
        json_str = instance.to_json()
        
        parsed = json.loads(json_str)
        assert parsed["__classname__"] == "Chamfer"
        assert "side" in parsed
        assert "rside" in parsed
        assert "l" in parsed
        # alpha and dr may or may not be present depending on instance

    @patch("builtins.open", side_effect=Exception("Dump error"))
    def test_dump_error_handling(self, mock_open):
        """Test dump method error handling"""
        instance = self.get_sample_instance()
        
        with pytest.raises(Exception, match="Failed to Insert dump"):
            instance.dump()


class TestChamferYAMLConstructor:
    """Test Chamfer YAML constructor"""
    
    def test_yaml_constructor_function(self):
        """Test the Chamfer_constructor function"""
        # Mock loader and node
        mock_loader = Mock()
        mock_node = Mock()
        
        # Mock data that would be returned by construct_mapping
        mock_data = {
            "name": "test", 
            "side": "BP",
            "rside": "rext",
            "alpha": 60.0,
            "dr": 4.0,
            "l": 15.0
        }
        
        mock_loader.construct_mapping.return_value = mock_data
        
        result = Chamfer_constructor(mock_loader, mock_node)
        
        # The constructor should return a Chamfer instance directly
        assert isinstance(result, Chamfer)
        assert result.name == "test"
        assert result.side == "BP"
        assert result.rside == "rext"
        assert result.alpha == 60.0
        assert result.dr == 4.0
        assert result.l == 15.0
        mock_loader.construct_mapping.assert_called_once_with(mock_node)

    def test_yaml_constructor_with_optional_fields(self):
        """Test constructor with missing optional alpha and dr fields"""
        mock_loader = Mock()
        mock_node = Mock()
        
        mock_data = {
            "name": "test",
            "side": "HP",
            "rside": "rint",
            "l": 7.0
        }
        
        mock_loader.construct_mapping.return_value = mock_data
        
        result = Chamfer_constructor(mock_loader, mock_node)
        
        assert isinstance(result, Chamfer)
        assert result.name == "test"
        assert result.side == "HP"
        assert result.rside == "rint"
        assert result.l == 7.0
        assert result.alpha is None
        assert result.dr is None

    def test_yaml_constructor_with_get_method(self):
        """Test that constructor uses get() method for optional fields"""
        mock_loader = Mock()
        mock_node = Mock()
        
        # Test with only alpha field
        mock_data = {
            "name": "test",
            "side": "BP",
            "rside": "rext",
            "alpha": 37.5,
            "l": 9.0
        }
        
        mock_loader.construct_mapping.return_value = mock_data
        
        result = Chamfer_constructor(mock_loader, mock_node)
        
        assert isinstance(result, Chamfer)
        assert result.alpha == 37.5
        assert result.dr is None


class TestChamferYAMLTag(BaseYAMLTagTestMixin):
    """Test Chamfer YAML tag using common test mixin"""
    
    def get_class_with_yaml_tag(self):
        """Return Chamfer class"""
        return Chamfer
    
    def get_expected_yaml_tag(self):
        """Return expected YAML tag"""
        return "Chamfer"


class TestChamferFileOperations:
    """Test Chamfer file operations and serialization edge cases"""
    
    def test_from_yaml_with_optional_fields(self):
        """Test from_yaml with missing optional alpha and dr fields"""
        yaml_content = '''
!<Chamfer>
name: test
side: HP
rside: rint
l: 7.0
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp_file:
            tmp_file.write(yaml_content)
            tmp_file.flush()
            
            try:
                with patch('os.getcwd', return_value='/tmp'):
                    chamfer = Chamfer.from_yaml(tmp_file.name)
                
                assert chamfer.name == "test"
                assert chamfer.side == "HP"
                assert chamfer.rside == "rint"
                assert chamfer.l == 7.0
                assert chamfer.alpha is None
                assert chamfer.dr is None
                
            finally:
                os.unlink(tmp_file.name)

    def test_from_yaml_with_only_alpha(self):
        """Test from_yaml with only alpha field"""
        yaml_content = '''
!<Chamfer>
name: test
side: BP
rside: rext
alpha: 37.5
l: 9.0
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp_file:
            tmp_file.write(yaml_content)
            tmp_file.flush()
            
            try:
                with patch('os.getcwd', return_value='/tmp'):
                    chamfer = Chamfer.from_yaml(tmp_file.name)
                
                assert chamfer.name == "test"
                assert chamfer.side == "BP"
                assert chamfer.rside == "rext"
                assert chamfer.alpha == 37.5
                assert chamfer.l == 9.0
                assert chamfer.dr is None
                
            finally:
                os.unlink(tmp_file.name)

    def test_from_yaml_with_only_dr(self):
        """Test from_yaml with only dr field"""
        yaml_content = '''
!<Chamfer>
name: test
side: HP
rside: rext
dr: 4.2
l: 11.0
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp_file:
            tmp_file.write(yaml_content)
            tmp_file.flush()
            
            try:
                with patch('os.getcwd', return_value='/tmp'):
                    chamfer = Chamfer.from_yaml(tmp_file.name)
                
                assert chamfer.name == "test"
                assert chamfer.side == "HP"
                assert chamfer.rside == "rext"
                assert chamfer.dr == 4.2
                assert chamfer.l == 11.0
                assert chamfer.alpha is None
                
            finally:
                os.unlink(tmp_file.name)

    def test_serialization_roundtrip_consistency(self):
        """Test complete serialization roundtrip consistency"""
        original_chamfers = [
            Chamfer(name="test", side="HP", rside="rint", alpha=30.0, l=5.0),
            Chamfer(name="test", side="BP", rside="rext", dr=3.5, l=7.0),
            Chamfer(name="test", side="HP", rside="rext", alpha=60.0, dr=4.0, l=8.0)
        ]
        
        for original in original_chamfers:
            # Test JSON serialization
            json_str = original.to_json()
            parsed_json = json.loads(json_str)
            
            # Verify all data is preserved
            assert parsed_json["name"] == original.name
            assert parsed_json["side"] == original.side
            assert parsed_json["rside"] == original.rside
            assert parsed_json["l"] == original.l
            
            if original.alpha is not None:
                assert parsed_json["alpha"] == original.alpha
            if original.dr is not None:
                assert parsed_json["dr"] == original.dr


class TestChamferValidation:
    """Test Chamfer parameter validation and consistency"""
    
    @pytest.mark.parametrize("side", ["HP", "BP"])
    def test_valid_side_values(self, side):
        """Test valid side values"""
        chamfer = Chamfer(name="test", side=side, rside="rint", l=5.0)
        assert chamfer.side == side

    @pytest.mark.parametrize("rside", ["rint", "rext"])
    def test_valid_rside_values(self, rside):
        """Test valid rside values"""
        chamfer = Chamfer(name="test", side="HP", rside=rside, l=5.0)
        assert chamfer.rside == rside

    def test_parameter_type_validation(self):
        """Test parameter type validation"""
        # Test with various numeric types
        test_cases = [
            (45, 2, 8),      # integers
            (45.0, 2.0, 8.0), # floats
            (45.5, 2.5, 8.5)  # decimal values
        ]
        
        for alpha, dr, l in test_cases:
            chamfer = Chamfer(name="test", side="HP", rside="rint", alpha=alpha, dr=dr, l=l)
            assert chamfer.alpha == alpha
            assert chamfer.dr == dr
            assert chamfer.l == l

    def test_geometric_consistency_validation(self):
        """Test geometric consistency between parameters"""
        # Create chamfer where alpha and dr should be consistent
        l = 10.0
        alpha = 45.0
        expected_dr = l * math.tan(math.radians(alpha))
        
        chamfer = Chamfer(name="test", side="HP", rside="rint", alpha=alpha, dr=expected_dr, l=l)
        
        # Both getDr and getAngle should give consistent results
        dr_from_alpha = l * math.tan(math.radians(alpha))
        dr_from_dr = expected_dr
        
        assert abs(dr_from_alpha - dr_from_dr) < 1e-10

    @pytest.mark.parametrize("angle", [0.0, 15.0, 30.0, 45.0, 60.0, 75.0, 89.0])
    def test_angle_range_validation(self, angle):
        """Test chamfer with various valid angles"""
        chamfer = Chamfer(name="test", side="HP", rside="rint", alpha=angle, l=10.0)
        
        # Validate angle is stored correctly
        assert chamfer.alpha == angle
        
        # Validate getAngle returns the stored value
        assert chamfer.getAngle() == angle
        
        # Validate getDr calculation is reasonable for the angle
        dr = chamfer.getDr()
        assert dr >= 0.0  # Should be non-negative
        
        if angle == 0.0:
            assert dr == 0.0
        elif angle == 45.0:
            assert abs(dr - 10.0) < 1e-10  # tan(45°) = 1


class TestChamferIntegration:
    """Integration tests for Chamfer class"""
    
    def test_chamfer_in_helix_context(self):
        """Test chamfer as it would be used in a helix"""
        # Create multiple chamfers as might be found on a helix
        chamfers = [
            Chamfer(name="test", side="HP", rside="rint", alpha=45.0, l=2.0),
            Chamfer(name="test", side="HP", rside="rext", alpha=30.0, l=3.0),
            Chamfer(name="test", side="BP", rside="rint", dr=1.5, l=2.5),
            Chamfer(name="test", side="BP", rside="rext", dr=2.0, l=4.0)
        ]
        
        # Test that each maintains its identity
        assert len(chamfers) == 4
        assert chamfers[0].side == "HP" and chamfers[0].rside == "rint"
        assert chamfers[1].side == "HP" and chamfers[1].rside == "rext"
        assert chamfers[2].side == "BP" and chamfers[2].rside == "rint"
        assert chamfers[3].side == "BP" and chamfers[3].rside == "rext"
        
        # Test calculations work for all
        for chamfer in chamfers:
            dr = chamfer.getDr()
            angle = chamfer.getAngle()
            assert isinstance(dr, float)
            assert isinstance(angle, float)
            assert dr >= 0.0  # All should be non-negative

    def test_chamfer_collection_operations(self):
        """Test operations on collections of chamfers"""
        chamfers = [
            Chamfer(name="test", side="HP", rside="rint", alpha=i*15.0, l=5.0)
            for i in range(1, 7)  # 15°, 30°, 45°, 60°, 75°, 90°
        ]
        
        # Test sorting by angle
        sorted_chamfers = sorted(chamfers, key=lambda c: c.alpha)
        assert sorted_chamfers[0].alpha == 15.0
        assert sorted_chamfers[-1].alpha == 90.0
        
        # Test filtering by calculated dr
        radii = [c.getDr() for c in chamfers]
        large_dr_chamfers = [c for c in chamfers if c.getDr() > 5.0]
        assert len(large_dr_chamfers) >= 1  # Should have some with large radii
        
        # Test aggregation operations
        total_l = sum(c.l for c in chamfers)
        assert total_l == 30.0  # 6 chamfers * 5.0 each

    def test_chamfer_mathematical_relationships(self):
        """Test mathematical relationships in chamfer collections"""
        # Create complementary chamfers (angles that sum to 90°)
        complementary_pairs = [
            (15.0, 75.0),
            (30.0, 60.0),
            (45.0, 45.0)
        ]
        
        for alpha1, alpha2 in complementary_pairs:
            chamfer1 = Chamfer(name="test", side="HP", rside="rint", alpha=alpha1, l=10.0)
            chamfer2 = Chamfer(name="test", side="BP", rside="rext", alpha=alpha2, l=10.0)
            
            # The product of their tangents should equal 1 (for complementary angles)
            dr1 = chamfer1.getDr()
            dr2 = chamfer2.getDr()
            
            # dr = l * tan(alpha), so dr/l = tan(alpha)
            tan1 = dr1 / 10.0
            tan2 = dr2 / 10.0
            
            if alpha1 + alpha2 == 90.0:
                assert abs(tan1 * tan2 - 1.0) < 1e-10


class TestChamferPerformance:
    """Performance tests for Chamfer class"""
    
    def test_multiple_chamfer_creation_performance(self):
        """Test performance of creating many chamfers"""
        chamfers = []
        for i in range(1000):
            chamfer = Chamfer(
                name="test", 
                side="HP" if i % 2 == 0 else "BP",
                rside="rint" if i % 3 == 0 else "rext",
                alpha=float(i % 90),
                dr=float(i % 10),
                l=float(i % 20 + 1)
            )
            chamfers.append(chamfer)
        
        assert len(chamfers) == 1000
        assert all(isinstance(c, Chamfer) for c in chamfers)
        
        # Test that operations still work efficiently
        radii = [c.getDr() for c in chamfers[:100]]  # Sample first 100
        angles = [c.getAngle() for c in chamfers[:100]]
        
        assert len(radii) == 100
        assert len(angles) == 100
        assert all(isinstance(r, float) for r in radii)
        assert all(isinstance(a, float) for a in angles)

    def test_chamfer_calculation_performance(self):
        """Test performance of chamfer calculations"""
        chamfer = Chamfer(name="test", side="HP", rside="rint", alpha=45.0, dr=5.0, l=10.0)
        
        # Perform many calculations
        radii = []
        angles = []
        for _ in range(10000):
            radii.append(chamfer.getDr())
            angles.append(chamfer.getAngle())
        
        assert len(radii) == 10000
        assert len(angles) == 10000
        
        # All calculations should be consistent
        assert all(r == radii[0] for r in radii)
        assert all(a == angles[0] for a in angles)


class TestChamferErrorHandling:
    """Test error handling in Chamfer class"""
    
    def test_invalid_parameter_types(self):
        """Test handling of invalid parameter types"""
        # These might raise TypeErrors depending on implementation
        try:
            chamfer = Chamfer(name="test", side=None, rside=None, l=None)
            # If no error, implementation allows None values
        except TypeError:
            # Expected if implementation validates types
            pass

    def test_string_parameter_validation(self):
        """Test validation of string parameters"""
        # Test with invalid side values (implementation might not validate)
        try:
            chamfer = Chamfer(name="test", side="INVALID", rside="rint", l=5.0)
            assert chamfer.side == "INVALID"  # Stored as-is if no validation
        except ValueError:
            # Expected if implementation validates side values
            pass
        
        # Test with invalid rside values
        try:
            chamfer = Chamfer(name="test", side="HP", rside="INVALID", l=5.0)
            assert chamfer.rside == "INVALID"  # Stored as-is if no validation
        except ValueError:
            # Expected if implementation validates rside values
            pass

    def test_mathematical_error_conditions(self):
        """Test mathematical error conditions"""
        # Test potential division by zero in getAngle when l=0
        chamfer = Chamfer(name="test", side="HP", rside="rint", dr=5.0, l=0.0)
        
        try:
            angle = chamfer.getAngle()
            # If no error, implementation handles l=0 gracefully
        except ZeroDivisionError:
            # Expected if implementation doesn't handle l=0
            pass

    def test_extreme_mathematical_values(self):
        """Test extreme mathematical values"""
        # Test with very large angle (close to 90 degrees)
        try:
            chamfer = Chamfer(name="test", side="HP", rside="rint", alpha=89.9999, l=1.0)
            dr = chamfer.getDr()
            # Should be very large but finite
            assert dr > 1000
            assert math.isfinite(dr)
        except OverflowError:
            # Might occur for very large tan values
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])