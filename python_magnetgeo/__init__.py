"""Top-level package for Python Magnet Geometry."""

__author__ = """Christophe Trophime"""
__email__ = "christophe.trophime@lncmi.cnrs.fr"
__version__ = "1.0.0"

def list_registered_classes():
    """
    List all registered geometry classes.
    
    Useful for debugging and documentation.
    
    Returns:
        Dictionary of {class_name: class_object}
    """
    from .base import YAMLObjectBase
    return YAMLObjectBase.get_all_classes()


def verify_class_registration():
    """
    Verify that all expected classes are registered.
    
    Raises:
        AssertionError: If expected classes are missing
    """
    from .base import YAMLObjectBase
    
    expected_classes = [
        'Insert', 'Helix', 'Ring', 'Bitter', 'Supra', 'Supras', 
        'Bitters', 'Screen', 'MSite', 'Probe', 'Shape', 'ModelAxi',
        'Model3D', 'InnerCurrentLead', 'OuterCurrentLead', 'Contour2D',
        'Chamfer', 'Groove', 'Tierod', 'CoolingSlit'
    ]
    
    registered = YAMLObjectBase.get_all_classes()
    missing = [cls for cls in expected_classes if cls not in registered]
    
    if missing:
        raise AssertionError(
            f"Missing registered classes: {missing}\n"
            f"Registered: {list(registered.keys())}"
        )
    
    return True