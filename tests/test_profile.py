#!/usr/bin/env python3
"""
Test suite for Profile class
Tests creation, serialization, validation, and DAT file generation
"""

import os
import json
import tempfile
from pathlib import Path
import pytest

from python_magnetgeo.Profile import Profile
from python_magnetgeo.validation import ValidationError


class TestProfileCreation:
    """Test Profile object creation"""

    def test_basic_creation_with_labels(self):
        """Test creating a profile with explicit labels"""
        profile = Profile(
            cad="TEST-001",
            points=[[0, 0], [1, 0.5], [2, 0]],
            labels=[0, 1, 0]
        )

        assert profile.cad == "TEST-001"
        assert len(profile.points) == 3
        assert profile.points == [[0, 0], [1, 0.5], [2, 0]]
        assert profile.labels == [0, 1, 0]

    def test_creation_without_labels(self):
        """Test creating a profile without labels (should default to zeros)"""
        profile = Profile(
            cad="TEST-002",
            points=[[0, 0], [5, 2], [10, 0]]
        )

        assert profile.cad == "TEST-002"
        assert len(profile.points) == 3
        assert profile.labels == [0, 0, 0]  # Default to zeros

    def test_creation_with_none_labels(self):
        """Test creating a profile with labels=None"""
        profile = Profile(
            cad="TEST-003",
            points=[[0, 0], [1, 1]],
            labels=None
        )

        assert profile.labels == [0, 0]

    def test_labels_length_mismatch_raises_error(self):
        """Test that mismatched labels length raises ValueError"""
        with pytest.raises(ValueError, match="Labels length.*must match points length"):
            Profile(
                cad="TEST-004",
                points=[[0, 0], [1, 1], [2, 2]],
                labels=[0, 1]  # Only 2 labels for 3 points
            )


class TestProfileRepr:
    """Test Profile string representation"""

    def test_repr_with_labels(self):
        """Test __repr__ with explicit labels"""
        profile = Profile(
            cad="REPR-001",
            points=[[0, 0], [1, 1]],
            labels=[0, 1]
        )

        repr_str = repr(profile)
        assert "Profile" in repr_str
        assert "REPR-001" in repr_str
        assert "[[0, 0], [1, 1]]" in repr_str
        assert "[0, 1]" in repr_str

    def test_repr_without_labels(self):
        """Test __repr__ with default labels"""
        profile = Profile(
            cad="REPR-002",
            points=[[0, 0], [1, 1]]
        )

        repr_str = repr(profile)
        assert "Profile" in repr_str
        assert "REPR-002" in repr_str


class TestProfileSerialization:
    """Test Profile serialization to JSON and YAML"""

    def test_to_json(self):
        """Test JSON serialization"""
        profile = Profile(
            cad="JSON-001",
            points=[[-5.34, 0], [0, 0.9], [5.34, 0]],
            labels=[0, 1, 0]
        )

        json_str = profile.to_json()
        parsed = json.loads(json_str)

        assert parsed["cad"] == "JSON-001"
        assert parsed["points"] == [[-5.34, 0], [0, 0.9], [5.34, 0]]
        assert parsed["labels"] == [0, 1, 0]
        assert parsed["__classname__"] == "Profile"

    def test_to_json_without_labels(self):
        """Test JSON serialization with default labels"""
        profile = Profile(
            cad="JSON-002",
            points=[[0, 0], [1, 0.5], [2, 0]]
        )

        json_str = profile.to_json()
        parsed = json.loads(json_str)

        assert parsed["cad"] == "JSON-002"
        assert parsed["labels"] == [0, 0, 0]

    def test_from_dict_with_labels(self):
        """Test creating Profile from dictionary with labels"""
        data = {
            "cad": "DICT-001",
            "points": [[0, 0], [5, 2], [10, 0]],
            "labels": [0, 1, 0]
        }

        profile = Profile.from_dict(data)

        assert profile.cad == "DICT-001"
        assert profile.points == [[0, 0], [5, 2], [10, 0]]
        assert profile.labels == [0, 1, 0]

    def test_from_dict_without_labels(self):
        """Test creating Profile from dictionary without labels"""
        data = {
            "cad": "DICT-002",
            "points": [[0, 0], [1, 1], [2, 0]]
        }

        profile = Profile.from_dict(data)

        assert profile.cad == "DICT-002"
        assert profile.labels == [0, 0, 0]

    def test_json_round_trip(self):
        """Test JSON serialization round trip"""
        original = Profile(
            cad="ROUNDTRIP-001",
            points=[[-5.34, 0], [-3.34, 0], [0, 0.9], [3.34, 0], [5.34, 0]],
            labels=[0, 0, 1, 0, 0]
        )

        json_str = original.to_json()
        parsed = json.loads(json_str)
        reconstructed = Profile.from_dict(parsed)

        assert reconstructed.cad == original.cad
        assert reconstructed.points == original.points
        assert reconstructed.labels == original.labels

    def test_yaml_round_trip(self):
        """Test YAML serialization round trip"""
        original = Profile(
            cad="Profile0",
            points=[[0, 0], [5, 2], [10, 0]],
            labels=[0, 1, 0]
        )

        # Write to file and load back
        with tempfile.TemporaryDirectory() as tmpdir:
            # Change to temp directory for the test
            original_dir = os.getcwd()
            os.chdir(tmpdir)

            try:
                # Dump to YAML (creates Profile.yaml)
                original.write_to_yaml()
                assert os.path.exists("Profile0.yaml")

                # Load it back
                loaded = Profile.from_yaml("Profile0.yaml")

                assert loaded.cad == original.cad
                assert loaded.points == original.points
                assert loaded.labels == original.labels
            finally:
                os.chdir(original_dir)


class TestProfileDATGeneration:
    """Test DAT file generation"""

    def test_generate_dat_with_labels(self):
        """Test DAT file generation with labels"""
        profile = Profile(
            cad="HR-54-116",
            points=[[-5.34, 0], [-3.34, 0], [0, 0.9], [3.34, 0], [5.34, 0]],
            labels=[0, 0, 1, 0, 0]
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = profile.generate_dat_file(tmpdir)

            assert output_path.exists()
            assert output_path.name == "Shape_HR-54-116.dat"

            # Read and verify content
            content = output_path.read_text()

            # Check header
            assert "#Shape : HR-54-116" in content
            assert "# Profile with region labels" in content

            # Check column headers
            assert "#X_i F_i\tId_i" in content

            # Check point count
            assert "5" in content

            # Check data points with labels
            lines = content.split('\n')
            data_lines = [l for l in lines if l and not l.startswith('#')]
            assert len(data_lines) >= 5  # 1 for count, 5 for points

    def test_generate_dat_without_labels(self):
        """Test DAT file generation without labels (or all-zero labels)"""
        profile = Profile(
            cad="SIMPLE-AIRFOIL",
            points=[[0, 0], [0.5, 0.05], [1, 0.03]],
            labels=None  # No labels
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = profile.generate_dat_file(tmpdir)

            assert output_path.exists()
            assert output_path.name == "Shape_SIMPLE-AIRFOIL.dat"

            # Read and verify content
            content = output_path.read_text()

            # Check header
            assert "#Shape : SIMPLE-AIRFOIL" in content
            assert "# Profile geometry" in content

            # Check column headers - should NOT have Id_i column
            assert "#X_i F_i\n" in content
            assert "Id_i" not in content

            # Verify data lines don't have labels
            lines = content.split('\n')
            data_lines = [l for l in lines if l and not l.startswith('#') and len(l.strip()) > 0]
            # First data line is the count
            # Subsequent lines should have 2 values only (X, F)
            for line in data_lines[1:]:
                parts = line.split()
                if len(parts) > 0:  # Skip empty lines
                    # Should be 2 values (X, F), not 3
                    assert len(parts) <= 2, f"Expected 2 values without labels, got {len(parts)}: {line}"

    def test_generate_dat_all_zero_labels(self):
        """Test that all-zero labels are treated as no labels"""
        profile = Profile(
            cad="ZERO-LABELS",
            points=[[0, 0], [1, 0.5], [2, 0]],
            labels=[0, 0, 0]  # All zeros
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = profile.generate_dat_file(tmpdir)
            content = output_path.read_text()

            # Should be treated as no labels
            assert "# Profile geometry" in content
            assert "#X_i F_i\n" in content
            assert "Id_i" not in content

    def test_generate_dat_mixed_labels(self):
        """Test DAT file with mixed zero and non-zero labels"""
        profile = Profile(
            cad="MIXED-LABELS",
            points=[[0, 0], [1, 0.5], [2, 0.3], [3, 0]],
            labels=[0, 1, 2, 0]  # Has non-zero labels
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = profile.generate_dat_file(tmpdir)
            content = output_path.read_text()

            # Should include labels column
            assert "# Profile with region labels" in content
            assert "#X_i F_i\tId_i" in content

    def test_generate_dat_custom_directory(self):
        """Test DAT file generation in custom directory"""
        profile = Profile(
            cad="CUSTOM-DIR",
            points=[[0, 0], [1, 1]]
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            custom_dir = Path(tmpdir) / "custom" / "path"
            custom_dir.mkdir(parents=True)

            output_path = profile.generate_dat_file(str(custom_dir))

            assert output_path.exists()
            assert output_path.parent == custom_dir

    def test_dat_file_format_precision(self):
        """Test that DAT file uses correct precision (2 decimal places)"""
        profile = Profile(
            cad="PRECISION-TEST",
            points=[[1.234567, 2.345678], [3.456789, 4.567890]],
            labels=[0, 1]
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = profile.generate_dat_file(tmpdir)
            content = output_path.read_text()

            # Check that values are formatted with 2 decimal places
            assert "1.23" in content
            assert "2.35" in content
            assert "3.46" in content
            assert "4.57" in content


class TestProfileValidation:
    """Test Profile validation"""

    def test_empty_points_list(self):
        """Test that empty points list is handled"""
        # Should work but create empty labels
        profile = Profile(
            cad="EMPTY-POINTS",
            points=[]
        )
        assert profile.points == []
        assert profile.labels == []

    def test_single_point(self):
        """Test profile with single point"""
        profile = Profile(
            cad="SINGLE-POINT",
            points=[[0, 0]],
            labels=[1]
        )
        assert len(profile.points) == 1
        assert len(profile.labels) == 1


class TestProfileInheritance:
    """Test that Profile inherits from YAMLObjectBase correctly"""

    def test_has_yaml_methods(self):
        """Test that Profile has all YAML serialization methods"""
        profile = Profile(cad="TEST", points=[[0, 0]])

        assert hasattr(profile, 'write_to_yaml')
        assert hasattr(profile, 'to_json')
        assert hasattr(profile, 'write_to_json')
        assert hasattr(Profile, 'from_yaml')
        assert hasattr(Profile, 'from_json')
        assert hasattr(Profile, 'from_dict')

    def test_yaml_tag(self):
        """Test that Profile has correct YAML tag"""
        assert Profile.yaml_tag == "Profile"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
