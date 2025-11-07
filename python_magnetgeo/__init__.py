"""
python_magnetgeo - Python library for magnet geometry management

This package provides lazy loading of geometry classes.
Import the package once and access all classes through the module namespace.

Usage:
    import python_magnetgeo as pmg
    
    # Load from YAML with automatic type detection
    geometry = pmg.load("config.yaml")
    
    # Or create directly
    helix = pmg.Helix(name="H1", r=[10, 20], z=[0, 50])
    ring = pmg.Ring(name="R1", r=[5, 15], z=[0, 10])
"""

__author__ = "Christophe Trophime"
__email__ = "christophe.trophime@lncmi.cnrs.fr"

# Version is read from package metadata (defined in pyproject.toml)
# This ensures a single source of truth for the version number
try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # Fallback for Python < 3.8 (though we require 3.11+)
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("python-magnetgeo")
except PackageNotFoundError:
    # Package not installed (e.g., running from source without install)
    # This is expected during development before running `pip install -e .`
    __version__ = "0.0.0+unknown"

# Import core utilities and base classes immediately
from .base import YAMLObjectBase, SerializableMixin
from .validation import ValidationError, ValidationWarning, GeometryValidator
from .utils import getObject as load, loadObject

# Define what gets imported with "from python_magnetgeo import *"
__all__ = [
    # Core functionality
    'load',
    'loadObject',
    'list_registered_classes',
    'verify_class_registration',
    
    # Base classes and validation
    'YAMLObjectBase',
    'SerializableMixin',
    'ValidationError',
    'ValidationWarning',
    'GeometryValidator',
    
    # Geometry classes (lazy loaded)
    'Insert',
    'Helix',
    'Ring',
    'Bitter',
    'Supra',
    'Supras',
    'Bitters',
    'Screen',
    'MSite',
    'Probe',
    'Shape',
    'ModelAxi',
    'Model3D',
    'InnerCurrentLead',
    'OuterCurrentLead',
    'Contour2D',
    'Chamfer',
    'Groove',
    'Tierod',
    'CoolingSlit',
]

# Lazy loading map: maps class names to their module paths
_LAZY_IMPORTS = {
    'Insert': 'Insert',
    'Helix': 'Helix',
    'Ring': 'Ring',
    'Bitter': 'Bitter',
    'Supra': 'Supra',
    'Supras': 'Supra',
    'Bitters': 'Bitter',
    'Screen': 'Screen',
    'MSite': 'MSite',
    'Probe': 'Probe',
    'Shape': 'Shape',
    'ModelAxi': 'ModelAxi',
    'Model3D': 'Model3D',
    'InnerCurrentLead': 'CurrentLead',
    'OuterCurrentLead': 'CurrentLead',
    'Contour2D': 'Contour2D',
    'Chamfer': 'Chamfer',
    'Groove': 'Groove',
    'Tierod': 'Tierod',
    'CoolingSlit': 'CoolingSlit',
}

# Cache for loaded modules
_loaded_classes = {}


def __getattr__(name):
    """
    Lazy loading implementation.
    
    This function is called when an attribute is not found in the module.
    We use it to lazily import geometry classes only when they're accessed.
    
    Args:
        name: Attribute name being accessed
        
    Returns:
        The requested class or raises AttributeError
        
    Example:
        >>> import python_magnetgeo as pmg
        >>> helix = pmg.Helix(...)  # Helix is imported here, not at initial import
    """
    # Check if it's a known geometry class
    if name in _LAZY_IMPORTS:
        # Check cache first
        if name in _loaded_classes:
            return _loaded_classes[name]
        
        # Import the module
        module_name = _LAZY_IMPORTS[name]
        try:
            module = __import__(f'python_magnetgeo.{module_name}', 
                              fromlist=[name])
            cls = getattr(module, name)
            
            # Cache it
            _loaded_classes[name] = cls
            return cls
            
        except (ImportError, AttributeError) as e:
            raise AttributeError(
                f"Failed to lazy load class '{name}' from module "
                f"'{module_name}': {e}"
            ) from e
    
    # Not a lazy import - raise normal AttributeError
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def __dir__():
    """
    Return list of available attributes for tab-completion.
    
    This ensures that IDEs and interactive shells can see all available
    classes even though they're lazy loaded.
    """
    # Start with standard module attributes
    attrs = list(globals().keys())
    
    # Add all lazy-loadable classes
    attrs.extend(_LAZY_IMPORTS.keys())
    
    return sorted(set(attrs))


def list_registered_classes():
    """
    List all registered geometry classes.
    
    Useful for debugging and discovering available geometry types.
    
    Returns:
        Dictionary of {class_name: class_object}
        
    Example:
        >>> import python_magnetgeo as pmg
        >>> classes = pmg.list_registered_classes()
        >>> print(classes.keys())
        dict_keys(['Insert', 'Helix', 'Ring', ...])
    """
    return YAMLObjectBase.get_all_classes()


def verify_class_registration():
    """
    Verify that all expected classes are registered with YAML system.
    
    This is mainly for testing and validation. It imports all classes
    to ensure they're properly registered as YAML types.
    
    Raises:
        AssertionError: If expected classes are missing
        
    Returns:
        True if all classes are registered
        
    Example:
        >>> import python_magnetgeo as pmg
        >>> pmg.verify_class_registration()
        True
    """
    expected_classes = [
        'Insert', 'Helix', 'Ring', 'Bitter', 'Supra', 'Supras', 
        'Bitters', 'Screen', 'MSite', 'Probe', 'Shape', 'ModelAxi',
        'Model3D', 'InnerCurrentLead', 'OuterCurrentLead', 'Contour2D',
        'Chamfer', 'Groove', 'Tierod', 'CoolingSlit'
    ]
    
    # Force loading of all classes
    for class_name in expected_classes:
        try:
            getattr(__import__(__name__), class_name)
        except AttributeError:
            pass  # Will be caught below
    
    # Check registration
    registered = YAMLObjectBase.get_all_classes()
    missing = [cls for cls in expected_classes if cls not in registered]
    
    if missing:
        raise AssertionError(
            f"Missing registered classes: {missing}\n"
            f"Registered: {list(registered.keys())}"
        )
    
    return True


# Re-export commonly used functions at package level
# These are always imported (not lazy) since they're frequently used
def load_yaml(filename: str, debug: bool = False):
    """
    Load any geometry object from YAML file with automatic type detection.
    
    This is an alias for getObject() for convenience.
    
    Args:
        filename: Path to YAML file
        debug: Enable debug output
        
    Returns:
        Geometry object (type depends on YAML content)
        
    Example:
        >>> obj = pmg.load_yaml("config.yaml")
        >>> print(type(obj).__name__)
        'Insert'
    """
    return load(filename, debug=debug)


# Backwards compatibility aliases
getObject = load
loadYaml = load_yaml