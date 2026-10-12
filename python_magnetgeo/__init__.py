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
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    # Fallback for Python < 3.8 (though we require 3.11+)
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("python-magnetgeo")
except PackageNotFoundError:
    # Package not installed (e.g., running from source without install)
    # This is expected during development before running `pip install -e .`
    __version__ = "0.0.0+unknown"

# Import logging configuration
# Import core utilities and base classes immediately
from .base import SerializableMixin, YAMLObjectBase
from .Bitter import Bitter
from .Bitters import Bitters
from .Chamfer import Chamfer
from .Contour2D import Contour2D
from .coolingslit import CoolingSlit
from .Groove import Groove
from .Helix import Helix
from .InnerCurrentLead import InnerCurrentLead

# Import all geometry classes eagerly so their YAML constructors are registered
# before any yaml.load() call is made. Lazy loading breaks YAML deserialization
# because constructors are only registered when the class is first imported.
from .Insert import Insert
from .logging_config import (
    CRITICAL,
    DEBUG,
    ERROR,
    INFO,
    WARNING,
    configure_logging,
    disable_logging,
    enable_logging,
    get_logger,
    set_level,
)
from .Model3D import Model3D
from .ModelAxi import ModelAxi
from .Assembly import Assembly
from .OuterCurrentLead import OuterCurrentLead
from .Probe import Probe
from .Ring import Ring
from .Screen import Screen
from .Shape import Shape
from .Supra import Supra
from .Supras import Supras
from .tierod import Tierod
from .utils import ObjectLoadError, UnsupportedTypeError, loadObject
from .utils import getObject as load
from .validation import GeometryValidator, ValidationError, ValidationWarning

MSite = Assembly  # deprecated alias — remove after one release

# Define what gets imported with "from python_magnetgeo import *"
__all__ = [
    # Core functionality
    "load",
    "loadObject",
    "list_registered_classes",
    "verify_class_registration",
    # Logging
    "configure_logging",
    "get_logger",
    "set_level",
    "disable_logging",
    "enable_logging",
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
    # Base classes and validation
    "YAMLObjectBase",
    "SerializableMixin",
    "ValidationError",
    "ValidationWarning",
    "GeometryValidator",
    # Exceptions
    "ObjectLoadError",
    "UnsupportedTypeError",
    # Geometry classes
    "Insert",
    "Helix",
    "Ring",
    "Bitter",
    "Supra",
    "Supras",
    "Bitters",
    "Screen",
    "Assembly",
    "Probe",
    "Shape",
    "ModelAxi",
    "Model3D",
    "InnerCurrentLead",
    "OuterCurrentLead",
    "Contour2D",
    "Chamfer",
    "Groove",
    "Tierod",
    "CoolingSlit",
]


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
        "Insert",
        "Helix",
        "Ring",
        "Bitter",
        "Supra",
        "Supras",
        "Bitters",
        "Screen",
        "Assembly",
        "Probe",
        "Shape",
        "ModelAxi",
        "Model3D",
        "InnerCurrentLead",
        "OuterCurrentLead",
        "Contour2D",
        "Chamfer",
        "Groove",
        "Tierod",
        "CoolingSlit",
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
            f"Missing registered classes: {missing}\n" f"Registered: {list(registered.keys())}"
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
