#!/usr/bin/env python3
"""
Unit tests for get_required_files() dry-run dependency analysis.
"""

import unittest
from python_magnetgeo.Helix import Helix


class TestGetRequiredFiles(unittest.TestCase):
    """Test the get_required_files() method for dependency analysis."""

    def test_all_file_references(self):
        """Test configuration with all nested objects as file references."""
        config = {
            "name": "H1",
            "r": [15.0, 25.0],
            "z": [0.0, 100.0],
            "cutwidth": 2.0,
            "odd": True,
            "dble": False,
            "modelaxi": "modelaxi_file",
            "model3d": "model3d_file",
            "shape": "shape_file",
            "chamfers": ["chamfer1", "chamfer2"],
            "grooves": "grooves_file",
        }

        files = Helix.get_required_files(config)

        expected = {
            "modelaxi_file.yaml",
            "model3d_file.yaml",
            "shape_file.yaml",
            "chamfer1.yaml",
            "chamfer2.yaml",
            "grooves_file.yaml",
        }

        self.assertEqual(files, expected)

    def test_all_inline_definitions(self):
        """Test configuration with all nested objects as inline dicts."""
        config = {
            "name": "H2",
            "r": [20.0, 30.0],
            "z": [10.0, 110.0],
            "cutwidth": 2.5,
            "odd": False,
            "dble": True,
            "modelaxi": {
                "num": 10,
                "h": 8.0,
                "turns": [0.29] * 10,
            },
            "model3d": {
                "with_shapes": False,
                "with_channels": False,
            },
            "shape": None,
            "chamfers": None,
            "grooves": None,
        }

        files = Helix.get_required_files(config)

        # Should be empty since all are inline or None
        self.assertEqual(files, set())

    def test_mixed_references(self):
        """Test configuration with mixed file references and inline objects."""
        config = {
            "name": "H3",
            "r": [25.0, 35.0],
            "z": [20.0, 120.0],
            "cutwidth": 3.0,
            "odd": True,
            "dble": False,
            "modelaxi": "modelaxi_ref",  # File
            "model3d": {  # Inline
                "with_shapes": True,
                "with_channels": True,
            },
            "shape": "shape_ref",  # File
            "chamfers": [
                "chamfer_ref",  # File
                {  # Inline
                    "name": "inline_chamfer",
                    "dr": 1.0,
                    "dz": 1.0,
                },
            ],
            "grooves": {  # Inline
                "gtype": "rint",
                "n": 12,
                "eps": 2.0,
            },
        }

        files = Helix.get_required_files(config)

        expected = {
            "modelaxi_ref.yaml",
            "shape_ref.yaml",
            "chamfer_ref.yaml",
        }

        self.assertEqual(files, expected)

    def test_empty_config(self):
        """Test configuration with minimal required fields only."""
        config = {
            "name": "H_minimal",
            "r": [15.0, 25.0],
            "z": [0.0, 100.0],
            "cutwidth": 2.0,
            "odd": True,
            "dble": False,
        }

        files = Helix.get_required_files(config)

        # No nested objects specified - should be empty
        self.assertEqual(files, set())

    def test_none_values(self):
        """Test configuration with explicit None values."""
        config = {
            "name": "H_none",
            "r": [15.0, 25.0],
            "z": [0.0, 100.0],
            "cutwidth": 2.0,
            "odd": True,
            "dble": False,
            "modelaxi": None,
            "model3d": None,
            "shape": None,
            "chamfers": None,
            "grooves": None,
        }

        files = Helix.get_required_files(config)

        # All None - should be empty
        self.assertEqual(files, set())

    def test_empty_chamfers_list(self):
        """Test configuration with empty chamfers list."""
        config = {
            "name": "H_empty_list",
            "r": [15.0, 25.0],
            "z": [0.0, 100.0],
            "cutwidth": 2.0,
            "odd": True,
            "dble": False,
            "modelaxi": "modelaxi",
            "chamfers": [],  # Empty list
        }

        files = Helix.get_required_files(config)

        expected = {"modelaxi.yaml"}
        self.assertEqual(files, expected)

    def test_debug_mode(self):
        """Test that debug mode doesn't affect results."""
        config = {
            "name": "H_debug",
            "r": [15.0, 25.0],
            "z": [0.0, 100.0],
            "cutwidth": 2.0,
            "odd": True,
            "dble": False,
            "modelaxi": "modelaxi",
            "shape": "shape",
        }

        # Get results with and without debug
        files_no_debug = Helix.get_required_files(config, debug=False)
        files_with_debug = Helix.get_required_files(config, debug=True)

        # Should be identical
        self.assertEqual(files_no_debug, files_with_debug)
        self.assertEqual(files_no_debug, {"modelaxi.yaml", "shape.yaml"})


if __name__ == "__main__":
    unittest.main()
