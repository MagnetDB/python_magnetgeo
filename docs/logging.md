# Logging in python_magnetgeo

The `python_magnetgeo` package includes comprehensive logging support to help you debug issues, monitor operations, and track the behavior of your geometry processing workflows.

## Quick Start

### Basic Usage

```python
import python_magnetgeo as pmg

# Configure logging (optional - uses INFO level by default)
pmg.configure_logging(level='INFO')

# Use the package normally - logs will be output to console
helix = pmg.Helix(name="H1", r=[10, 20], z=[0, 50])
helix.write_to_yaml()  # Will log: "Successfully wrote Helix to H1.yaml"
```

### Logging Levels

The package supports standard Python logging levels:

- `DEBUG`: Detailed information for diagnosing problems
- `INFO`: Confirmation that things are working as expected
- `WARNING`: Indication that something unexpected happened
- `ERROR`: A serious problem that prevented an operation
- `CRITICAL`: A very serious error

```python
import python_magnetgeo as pmg

# Set different log levels
pmg.configure_logging(level='DEBUG')   # Show everything
pmg.configure_logging(level='INFO')    # Show info and above
pmg.configure_logging(level='WARNING') # Show warnings and errors only
pmg.configure_logging(level='ERROR')   # Show errors only
```

## Advanced Configuration

### Logging to Files

Save logs to a file for later analysis:

```python
import python_magnetgeo as pmg

# Log to file and console
pmg.configure_logging(
    level='DEBUG',
    log_file='magnetgeo.log'
)

# Your code here - logs will be written to magnetgeo.log
```

### Different Levels for Console and File

You can have different logging levels for console output and file output:

```python
import python_magnetgeo as pmg

# Show only INFO on console, but log everything to file
pmg.configure_logging(
    console_level='INFO',
    file_level='DEBUG',
    log_file='debug.log'
)
```

### Disable Console Logging

Log only to a file, with no console output:

```python
import python_magnetgeo as pmg

pmg.configure_logging(
    console=False,
    log_file='operations.log',
    level='INFO'
)
```

### Custom Log Format

Choose from predefined formats or create your own:

```python
import python_magnetgeo as pmg
from python_magnetgeo.logging_config import DEFAULT_FORMAT, DETAILED_FORMAT, SIMPLE_FORMAT

# Use detailed format (includes function name and line number)
pmg.configure_logging(
    log_format=DETAILED_FORMAT,
    level='DEBUG'
)

# Use simple format (just level, name, message)
pmg.configure_logging(
    log_format=SIMPLE_FORMAT,
    level='INFO'
)

# Custom format
pmg.configure_logging(
    log_format='%(levelname)s - %(message)s',
    level='INFO'
)
```

## Runtime Control

### Change Log Level Dynamically

```python
import python_magnetgeo as pmg

# Initial configuration
pmg.configure_logging(level='INFO')

# ... some operations ...

# Increase verbosity for debugging
pmg.set_level('DEBUG')

# ... debug specific section ...

# Return to normal
pmg.set_level('INFO')
```

### Temporarily Disable Logging

```python
import python_magnetgeo as pmg

pmg.configure_logging(level='INFO')

# Disable all logging
pmg.disable_logging()

# ... operations without logging ...

# Re-enable logging
pmg.enable_logging()
```

## Using Logging in Your Own Code

If you're extending python_magnetgeo or using it in your own modules, you can use the same logging infrastructure:

```python
from python_magnetgeo.logging_config import get_logger

# Get a logger for your module
logger = get_logger(__name__)

def my_function():
    logger.debug("Starting my_function")
    logger.info("Processing data")
    logger.warning("Something unexpected")
    logger.error("An error occurred", exc_info=True)
```

## Log Format Examples

### Default Format
```
2026-01-23 10:30:45,123 - python_magnetgeo.utils - INFO - Successfully loaded Insert from data.yaml
```

### Detailed Format
```
2026-01-23 10:30:45,123 - python_magnetgeo.validation - ERROR - validate_name:115 - Validation failed: Name cannot be whitespace only
```

### Simple Format
```
INFO - python_magnetgeo.base - Writing Helix to H1.yaml
```

## Common Use Cases

### Debugging Failed YAML Loading

```python
import python_magnetgeo as pmg

# Enable detailed logging
pmg.configure_logging(level='DEBUG', log_format=pmg.logging_config.DETAILED_FORMAT)

try:
    obj = pmg.load("config.yaml")
except Exception as e:
    # Logs will show exactly where the loading failed
    print(f"Error: {e}")
```

### Tracking Validation Errors

```python
import python_magnetgeo as pmg

pmg.configure_logging(level='DEBUG')

try:
    # This will log detailed validation information
    helix = pmg.Helix(name="", r=[20, 10], z=[0, 50])  # Invalid: empty name and wrong r order
except pmg.ValidationError as e:
    print(f"Validation failed: {e}")
```

### Production Logging

For production use, log to a file with rotation:

```python
import python_magnetgeo as pmg
from pathlib import Path

# Create logs directory
Path("logs").mkdir(exist_ok=True)

# Configure for production
pmg.configure_logging(
    console_level='WARNING',     # Only show warnings/errors on console
    file_level='INFO',            # Log all operations to file
    log_file='logs/magnetgeo.log',
    log_format=pmg.logging_config.DEFAULT_FORMAT
)
```

## What Gets Logged

The package logs various operations at different levels:

### DEBUG Level
- File loading details (directories, paths)
- Validation checks (when they pass)
- Object attribute access
- Method entry/exit points

### INFO Level
- Successful file loads (YAML/JSON)
- Successful file writes
- Object creation
- Major operation completion

### WARNING Level
- Deprecated features
- Non-critical configuration issues
- Fallback behavior activation

### ERROR Level
- Validation failures
- File not found errors
- YAML/JSON parsing errors
- Type mismatches

## Environment Integration

### Integration with Application Logging

```python
import logging
import python_magnetgeo as pmg

# Configure your application's root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

# python_magnetgeo will use the same handlers
# No need to call configure_logging() unless you want different settings
```

### Suppressing Third-Party Logs

```python
import logging
import python_magnetgeo as pmg

# Configure python_magnetgeo logging
pmg.configure_logging(level='INFO')

# Suppress noisy third-party loggers
logging.getLogger('yaml').setLevel(logging.WARNING)
logging.getLogger('matplotlib').setLevel(logging.WARNING)
```

## Best Practices

1. **Configure Once**: Call `configure_logging()` once at application startup
2. **Use Appropriate Levels**: DEBUG for development, INFO for production
3. **Log to Files in Production**: Keep logs for troubleshooting
4. **Include Context**: When logging errors, use `exc_info=True` to include tracebacks
5. **Don't Over-Log**: Avoid logging in tight loops at INFO level
6. **Use Structured Messages**: Include relevant parameters in log messages

## Troubleshooting

### Logs Not Appearing

```python
import python_magnetgeo as pmg

# Make sure logging is configured
pmg.configure_logging(level='DEBUG')

# Check if logging is enabled
from python_magnetgeo.logging_config import is_configured
print(f"Logging configured: {is_configured()}")
```

### Too Many Debug Messages

```python
import python_magnetgeo as pmg

# Reduce verbosity
pmg.set_level('INFO')

# Or be more selective
pmg.set_level('DEBUG', 'python_magnetgeo.utils')  # Only debug utils
pmg.set_level('INFO')  # Everything else at INFO
```

### Check Current Log Level

```python
from python_magnetgeo.logging_config import get_log_level
import logging

level = get_log_level()
print(f"Current level: {logging.getLevelName(level)}")
```

## API Reference

### Main Functions

- `configure_logging(**kwargs)`: Configure logging for the package
- `get_logger(name)`: Get a logger instance for a module
- `set_level(level, logger_name=None)`: Change logging level
- `disable_logging()`: Disable all logging
- `enable_logging()`: Re-enable logging
- `is_configured()`: Check if logging is configured
- `get_log_level()`: Get current logging level

### Log Level Constants

- `DEBUG`: Constant for DEBUG level
- `INFO`: Constant for INFO level
- `WARNING`: Constant for WARNING level
- `ERROR`: Constant for ERROR level
- `CRITICAL`: Constant for CRITICAL level

### Format Constants

- `DEFAULT_FORMAT`: Standard format with timestamp, name, level, message
- `DETAILED_FORMAT`: Includes function name and line number
- `SIMPLE_FORMAT`: Just level, name, and message
