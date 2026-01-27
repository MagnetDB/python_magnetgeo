#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Examples of using the updated Insert, Bitters, and Supras classes with probes
"""

from python_magnetgeo.Insert import Insert
from python_magnetgeo.Bitters import Bitters
from python_magnetgeo.Supras import Supras
from python_magnetgeo.Probe import Probe
from python_magnetgeo.Helix import Helix
from python_magnetgeo.Ring import Ring

# Example 1: Create an Insert with embedded probes
def create_insert_with_probes():
    # Create some probes
    voltage_probes = Probe(
        name="H1_voltage_taps",
        probe_type="voltage_taps",
        index=["V1", "V2", "V3"],
        locations=[[15.2, 0.0, 10.5], [18.7, 0.0, 12.3], [22.1, 0.0, 14.1]]
    )
    
    temp_probes = Probe(
        name="H1_temperature", 
        probe_type="temperature",
        index=[1, 2],
        locations=[[16.5, 5.2, 11.0], [20.0, -3.1, 13.5]]
    )
    
    # Create insert with probes
    insert = Insert(
        name="M9_Insert",
        helices=["H1", "H2"],  # Will be loaded from YAML files
        rings=["R1"],
        currentleads=["inner_lead"],
        hangles=[0.0, 180.0],
        rangles=[0.0, 90.0, 180.0, 270.0],
        innerbore=12.5,
        outerbore=45.2,
        probes=[voltage_probes, temp_probes]  # Embedded probe objects
    )
    
    print("Insert with probes created:")
    print(f"  Number of probes: {len(insert.probes)}")
    for probe in insert.probes:
        print(f"    {probe.name}: {probe.get_probe_count()} {probe.probe_type} probes")
    
    return insert

# Example 2: Create Insert with probe references (strings)
def create_insert_with_probe_references():
    insert = Insert(
        name="M9_Insert_Refs",
        helices=["H1", "H2"],
        rings=["R1"], 
        currentleads=["inner_lead"],
        hangles=[0.0, 180.0],
        rangles=[0.0, 90.0, 180.0, 270.0],
        innerbore=12.5,
        outerbore=45.2,
        probes=["voltage_probes", "temp_probes"]  # String references to YAML files
    )
    
    # When update() is called, these strings will be converted to Probe objects
    # insert.update()  # This would load voltage_probes.yaml and temp_probes.yaml
    
    print("Insert with probe references created")
    return insert

# Example 3: Create Bitters with probes
def create_bitters_with_probes():
    bitter_probes = Probe(
        name="bitter_monitoring",
        probe_type="voltage_taps", 
        index=["BV1", "BV2"],
        locations=[[20.0, 0.0, 5.0], [30.0, 0.0, -5.0]]
    )
    
    bitters = Bitters(
        name="Bitter_Stack",
        magnets=["B1", "B2", "B3"],
        innerbore=8.0,
        outerbore=35.0,
        probes=[bitter_probes]
    )
    
    print("Bitters with probes created:")
    print(f"  Number of probes: {len(bitters.probes)}")
    
    return bitters

# Example 4: Create Supras with multiple probe types
def create_supras_with_probes():
    quench_probes = Probe(
        name="quench_detection",
        probe_type="voltage_taps",
        index=["Q1", "Q2", "Q3"],
        locations=[[18.0, 0.0, 10.0], [20.0, 0.0, 0.0], [22.0, 0.0, -10.0]]
    )
    
    temp_probes = Probe(
        name="hts_temperature",
        probe_type="temperature", 
        index=["T_HTS1", "T_HTS2"],
        locations=[[19.0, 2.0, 5.0], [21.0, -2.0, -5.0]]
    )
    
    supras = Supras(
        name="HTS_Stack",
        magnets=["S1", "S2"],
        innerbore=15.0,
        outerbore=25.0,
        probes=[quench_probes, temp_probes]
    )
    
    print("Supras with probes created:")
    print(f"  Number of probes: {len(supras.probes)}")
    for probe in supras.probes:
        print(f"    {probe.name}: {probe.get_probe_count()} {probe.probe_type} probes")
    
    return supras

# Example 5: Load from YAML with mixed probe types
def load_from_yaml_example():
    # This would load an Insert from YAML that contains both embedded probes
    # and string references to external probe files
    
    yaml_content = """
name: M9_Mixed_Probes
helices: ["H1", "H2"]
rings: ["R1"]
currentleads: ["inner_lead"]
hangles: [0.0, 180.0]
rangles: [0.0, 90.0, 180.0, 270.0]  
innerbore: 12.5
outerbore: 45.2
probes:
  - "external_voltage_probes"  # String reference
  - name: embedded_temp_probes  # Embedded probe
    probe_type: temperature
    index: [1, 2, 3]
    locations:
      - [16.5, 5.2, 11.0]
      - [20.0, -3.1, 13.5] 
      - [24.8, 2.7, 16.2]
"""
    
    # insert = Insert.from_yaml("mixed_probes.yaml")
    # insert.update()  # This would convert string references to Probe objects
    
    print("Example YAML structure for mixed probes shown above")

if __name__ == "__main__":
    print("=== Probe Integration Examples ===\n")
    
    # Run examples
    insert1 = create_insert_with_probes()
    print()
    
    insert2 = create_insert_with_probe_references()
    print()
    
    bitters = create_bitters_with_probes()
    print()
    
    supras = create_supras_with_probes()
    print()
    
    load_from_yaml_example()
    
    # Save examples to YAML
    print("\n=== Saving to YAML ===")
    insert1.write_to_yaml()
    bitters.write_to_yaml() 
    supras.write_to_yaml()
    print("YAML files created: M9_Insert.yaml, Bitter_Stack.yaml, HTS_Stack.yaml")