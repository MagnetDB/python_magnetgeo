#!/usr/bin/env python3
"""
Example demonstrating logging in python_magnetgeo

This script shows different logging configurations and their effects.
"""

import python_magnetgeo as pmg

def example_basic_logging():
    """Basic logging example"""
    print("\n=== Example 1: Basic Logging (INFO level) ===")
    
    # Configure with default INFO level
    pmg.configure_logging(level='INFO')
    
    # These operations will generate INFO-level logs
    helix = pmg.Helix(name="example_helix", r=[10, 20], z=[0, 50])
    print(f"Created: {helix.name}")
    
    # Save to file (will log)
    helix.dump()

def example_debug_logging():
    """Debug logging example"""
    print("\n=== Example 2: Debug Logging (shows all details) ===")
    
    # Enable DEBUG level for detailed information
    pmg.configure_logging(level='DEBUG')
    
    # Load a YAML file (shows detailed loading process)
    try:
        obj = pmg.load("data/HL-31_H1.yaml")
        print(f"Loaded: {obj.name if hasattr(obj, 'name') else 'unnamed'}")
    except Exception as e:
        print(f"Failed to load: {e}")

def example_file_logging():
    """Log to file example"""
    print("\n=== Example 3: Logging to File ===")
    
    # Log to both console and file
    pmg.configure_logging(
        level='INFO',
        log_file='magnetgeo_example.log'
    )
    
    print("Logs will be written to 'magnetgeo_example.log'")
    
    # Create some objects
    ring = pmg.Ring(name="example_ring", r=[5, 15], z=[0, 10])
    ring.dump()
    
    print("Check magnetgeo_example.log for detailed logs")

def example_different_levels():
    """Example with different levels for console and file"""
    print("\n=== Example 4: Different Levels for Console and File ===")
    
    # INFO on console, DEBUG in file
    pmg.configure_logging(
        console_level='INFO',
        file_level='DEBUG',
        log_file='detailed_debug.log'
    )
    
    print("Console shows INFO, file contains DEBUG details")
    
    # This will show INFO on console but DEBUG details in file
    try:
        helix = pmg.Helix(name="test", r=[10, 20], z=[0, 50])
        helix.dump()
    except Exception as e:
        print(f"Error: {e}")

def example_validation_logging():
    """Example showing validation error logging"""
    print("\n=== Example 5: Validation Error Logging ===")
    
    # Use DEBUG to see validation details
    pmg.configure_logging(level='DEBUG')
    
    print("Attempting to create invalid objects (will log errors):")
    
    # Empty name
    try:
        helix = pmg.Helix(name="", r=[10, 20], z=[0, 50])
    except pmg.ValidationError as e:
        print(f"  Caught: {e}")
    
    # Wrong order
    try:
        helix = pmg.Helix(name="test", r=[20, 10], z=[0, 50])  # r values descending
    except pmg.ValidationError as e:
        print(f"  Caught: {e}")
    
    # Wrong type
    try:
        helix = pmg.Helix(name="test", r="not a list", z=[0, 50])
    except pmg.ValidationError as e:
        print(f"  Caught: {e}")

def example_runtime_level_change():
    """Example of changing log level at runtime"""
    print("\n=== Example 6: Changing Log Level at Runtime ===")
    
    # Start with INFO
    pmg.configure_logging(level='INFO')
    print("Starting with INFO level")
    
    helix = pmg.Helix(name="test1", r=[10, 20], z=[0, 50])
    
    # Switch to DEBUG for detailed inspection
    print("\nSwitching to DEBUG level")
    pmg.set_level('DEBUG')
    
    helix2 = pmg.Helix(name="test2", r=[15, 25], z=[5, 55])
    
    # Back to WARNING (minimal output)
    print("\nSwitching to WARNING level (minimal output)")
    pmg.set_level('WARNING')
    
    helix3 = pmg.Helix(name="test3", r=[20, 30], z=[10, 60])
    print("Created test3 (no logs because WARNING level)")

def example_custom_format():
    """Example with custom log format"""
    print("\n=== Example 7: Custom Log Format ===")
    
    # Use detailed format with function names and line numbers
    from python_magnetgeo.logging_config import DETAILED_FORMAT
    
    pmg.configure_logging(
        level='DEBUG',
        log_format=DETAILED_FORMAT
    )
    
    print("Using detailed format (includes function:line)")
    
    helix = pmg.Helix(name="formatted", r=[10, 20], z=[0, 50])

def example_silent_mode():
    """Example of completely silent operation"""
    print("\n=== Example 8: Silent Mode (no logging) ===")
    
    # Configure logging first
    pmg.configure_logging(level='INFO')
    
    # Then disable it
    pmg.disable_logging()
    print("Logging disabled - no log output:")
    
    helix = pmg.Helix(name="silent", r=[10, 20], z=[0, 50])
    helix.dump()
    
    print("Operations completed without logs")
    
    # Re-enable
    pmg.enable_logging()
    print("Logging re-enabled")

def main():
    """Run all examples"""
    print("=" * 60)
    print("python_magnetgeo Logging Examples")
    print("=" * 60)
    
    try:
        example_basic_logging()
        example_debug_logging()
        example_file_logging()
        example_different_levels()
        example_validation_logging()
        example_runtime_level_change()
        example_custom_format()
        example_silent_mode()
        
        print("\n" + "=" * 60)
        print("All examples completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nExample failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
