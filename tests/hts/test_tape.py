#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Unit tests for Tape class.
"""

import pytest
import yaml
from pathlib import Path
from python_magnetgeo.hts import Tape


class TestTapeConstruction:
    """Test Tape object construction."""
    
    def test_default_construction(self):
        """Test construction with default values."""
        tape = Tape()
        assert tape.w == 0.0
        assert tape.h == 0.0
        assert tape.e == 0.0
    
    def test_full_construction(self):
        """Test construction with all parameters."""
        tape = Tape(w=12.0, h=0.1, e=0.05)
        assert tape.w == 12.0
        assert tape.h == 0.1
        assert tape.e == 0.05
    
    def test_negative_width_raises(self):
        """Test that negative width raises ValueError."""
        with pytest.raises(ValueError, match="width must be non-negative"):
            Tape(w=-1.0, h=0.1, e=0.05)
    
    def test_negative_height_raises(self):
        """Test that negative height raises ValueError."""
        with pytest.raises(ValueError, match="height must be non-negative"):
            Tape(w=12.0, h=-0.1, e=0.05)
    
    def test_negative_duromag_raises(self):
        """Test that negative duromag raises ValueError."""
        with pytest.raises(ValueError, match="Duromag thickness must be non-negative"):
            Tape(w=12.0, h=0.1, e=-0.05)


class TestTapeFromDict:
    """Test Tape.from_dict() construction."""
    
    def test_from_dict_full(self):
        """Test from_dict with all fields."""
        data = {'w': 12.0, 'h': 0.1, 'e': 0.05}
        tape = Tape.from_dict(data)
        assert tape.w == 12.0
        assert tape.h == 0.1
        assert tape.e == 0.05
    
    def test_from_dict_partial(self):
        """Test from_dict with missing optional fields."""
        data = {'w': 12.0, 'h': 0.1}
        tape = Tape.from_dict(data)
        assert tape.w == 12.0
        assert tape.h == 0.1
        assert tape.e == 0.0
    
    def test_from_dict_empty(self):
        """Test from_dict with empty dict uses defaults."""
        tape = Tape.from_dict({})
        assert tape.w == 0.0
        assert tape.h == 0.0
        assert tape.e == 0.0


class TestTapeProperties:
    """Test Tape properties."""
    
    def test_width_property(self):
        """Test width property."""
        tape = Tape(w=12.0, h=0.1, e=0.05)
        assert tape.width == 12.0
    
    def test_height_property(self):
        """Test height property."""
        tape = Tape(w=12.0, h=0.1, e=0.05)
        assert tape.height == 0.1
    
    def test_duromag_thickness_property(self):
        """Test duromag_thickness property."""
        tape = Tape(w=12.0, h=0.1, e=0.05)
        assert tape.duromag_thickness == 0.05
    
    def test_area_calculation(self):
        """Test area property calculation."""
        tape = Tape(w=12.0, h=0.1, e=0.05)
        assert tape.area == pytest.approx(1.2)  # 12.0 * 0.1
    
    def test_area_zero_dimensions(self):
        """Test area with zero dimensions."""
        tape = Tape(w=0.0, h=0.0, e=0.0)
        assert tape.area == 0.0


class TestTapeGetNames:
    """Test get_names method."""
    
    def test_get_names_returns_list(self):
        """Test get_names returns list with single name."""
        tape = Tape(w=12.0, h=0.1, e=0.05)
        names = tape.get_names("test_tape", "TAPE")
        assert isinstance(names, list)
        assert len(names) == 1
        assert names[0] == "test_tape"
    
    def test_get_names_ignores_detail(self):
        """Test that detail level doesn't affect tape names."""
        tape = Tape(w=12.0, h=0.1, e=0.05)
        names1 = tape.get_names("tape", "TAPE")
        names2 = tape.get_names("tape", "PANCAKE")
        assert names1 == names2


class TestTapeSerialization:
    """Test YAML serialization."""
    
    def test_yaml_tag(self):
        """Test yaml_tag is set correctly."""
        assert Tape.yaml_tag == "!Tape"
    
    def test_yaml_roundtrip(self, tmp_path):
        """Test YAML save and load roundtrip."""
        import os
        # Change to temp directory so dump() writes there
        original_dir = os.getcwd()
        try:
            os.chdir(tmp_path)
            
            # Create tape with a name (dump uses object name for filename)
            tape = Tape(w=12.0, h=0.1, e=0.05)
            # Since Tape is a dataclass without a name field,
            # dump() will use class name "Tape.yaml"
            tape.dump()
            
            # Load from YAML
            yaml_file = tmp_path / "Tape.yaml"
            loaded = Tape.from_yaml(str(yaml_file))
            
            assert loaded.w == tape.w
            assert loaded.h == tape.h
            assert loaded.e == tape.e
        finally:
            os.chdir(original_dir)
    
    def test_yaml_content_format(self, tmp_path):
        """Test YAML file contains correct format."""
        import os
        original_dir = os.getcwd()
        try:
            os.chdir(tmp_path)
            
            tape = Tape(w=12.0, h=0.1, e=0.05)
            tape.dump()
            
            yaml_file = tmp_path / "Tape.yaml"
            with open(yaml_file, 'r') as f:
                content = f.read()
            
            assert "!Tape" in content
            assert "w: 12.0" in content or "w: 12" in content
            assert "h: 0.1" in content
            assert "e: 0.05" in content
        finally:
            os.chdir(original_dir)


class TestTapeStringRepresentation:
    """Test string representations."""
    
    def test_repr(self):
        """Test __repr__ output."""
        tape = Tape(w=12.0, h=0.1, e=0.05)
        repr_str = repr(tape)
        assert "Tape" in repr_str
        assert "12.0" in repr_str
        assert "0.1" in repr_str
        assert "0.05" in repr_str
    
    def test_str(self):
        """Test __str__ output."""
        tape = Tape(w=12.0, h=0.1, e=0.05)
        str_output = str(tape)
        assert "Tape:" in str_output
        assert "width: 12.0 mm" in str_output
        assert "height: 0.1 mm" in str_output
        assert "duromag: 0.05 mm" in str_output
        assert "area:" in str_output


class TestTapeEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_zero_dimensions(self):
        """Test tape with all zero dimensions."""
        tape = Tape(w=0.0, h=0.0, e=0.0)
        assert tape.area == 0.0
        assert tape.width == 0.0
        assert tape.height == 0.0
    
    def test_large_dimensions(self):
        """Test tape with large dimensions."""
        tape = Tape(w=1000.0, h=10.0, e=5.0)
        assert tape.area == 10000.0
    
    def test_very_small_dimensions(self):
        """Test tape with very small dimensions."""
        tape = Tape(w=0.001, h=0.0001, e=0.00001)
        assert tape.area == pytest.approx(0.0000001)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
