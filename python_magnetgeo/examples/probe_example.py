#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Example usage of the Probe class
"""

from Probe import Probe

# Example 1: Create voltage tap probes
voltage_probes = Probe(
    name="H1_voltage_taps",
    probe_type="voltage_taps",
    index=["V1", "V2", "V3", "V4"],
    locations=[
        [10.5, 0.0, 15.2],
        [12.3, 0.0, 18.7],
        [14.1, 0.0, 22.1],
        [15.9, 0.0, 25.6]
    ]
)

# Example 2: Create temperature probes
temp_probes = Probe(
    name="H1_temperature",
    probe_type="temperature",
    index=[1, 2, 3],
    locations=[
        [11.0, 5.2, 16.5],
        [13.5, -3.1, 20.0],
        [16.2, 2.7, 24.8]
    ]
)

# Example 3: Create magnetic field probes
field_probes = Probe(
    name="center_field",
    probe_type="magnetic_field",
    index=["Bz_center", "Br_edge"],
    locations=[
        [0.0, 0.0, 0.0],     # Center of bore
        [5.0, 0.0, 0.0]      # Edge measurement
    ]
)

# Save to YAML files
voltage_probes.write_to_yaml()
temp_probes.write_to_yaml()
field_probes.write_to_yaml()

# Save to JSON files
voltage_probes.write_to_json()
temp_probes.write_to_json()
field_probes.write_to_json()

# Load from YAML
loaded_voltage = Probe.from_yaml("H1_voltage_taps.yaml")
print("Loaded voltage probes:", loaded_voltage)

# Access probe information
print(f"Number of voltage probes: {voltage_probes.get_probe_count()}")
print(f"V2 probe info: {voltage_probes.get_probe_by_index('V2')}")

# Add a new probe
voltage_probes.add_probe("V5", [17.8, 0.0, 29.1])
print(f"After adding V5: {voltage_probes.get_probe_count()} probes")

# Example YAML structure that would be saved:
yaml_example = """
name: H1_voltage_taps
probe_type: voltage_taps
index:
  - V1
  - V2
  - V3
  - V4
locations:
  - [10.5, 0.0, 15.2]
  - [12.3, 0.0, 18.7]
  - [14.1, 0.0, 22.1]
  - [15.9, 0.0, 25.6]
"""

print("Example YAML structure:")
print(yaml_example)