# Logging Support Added to python_magnetgeo

## Summary

Successfully added comprehensive logging support to the `python_magnetgeo` package. The implementation provides flexible, configurable logging capabilities throughout the entire codebase.

## Changes Made

### 1. New Module: `logging_config.py`
Created `/home/LNCMI-G/christophe.trophime/github/python_magnetgeo/python_magnetgeo/logging_config.py`

**Features:**
- `get_logger(name)`: Get a logger instance for any module
- `configure_logging(**kwargs)`: Configure logging with multiple options
  - Set log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - Log to console and/or file
  - Different levels for console vs file output
  - Custom log formats (DEFAULT, DETAILED, SIMPLE)
- `set_level(level)`: Change log level at runtime
- `disable_logging()` / `enable_logging()`: Toggle logging on/off
- Log level constants: DEBUG, INFO, WARNING, ERROR, CRITICAL

### 2. Updated `__init__.py`
Modified `/home/LNCMI-G/christophe.trophime/github/python_magnetgeo/python_magnetgeo/__init__.py`

- Imported all logging functions and constants
- Made them available at package level
- Added to `__all__` for proper exports

### 3. Enhanced Core Modules with Logging

#### Updated `utils.py`
- Added logger to module
- Logs file operations (YAML/JSON read/write)
- Logs errors with full context
- Logs directory changes during file loading

#### Updated `base.py`  
- Added logger import
- Ready for future logging enhancements

#### Updated `validation.py`
- Added logger to module
- Logs all validation checks at DEBUG level
- Logs validation failures at ERROR level with details
- Helps track down data issues

### 4. Documentation
Created comprehensive documentation:

- **`docs/logging.md`**: Full logging guide with examples
  - Quick start examples
  - Advanced configuration  
  - Runtime control
  - Common use cases
  - Troubleshooting
  - API reference

- **`examples/logging_examples.py`**: Executable examples demonstrating:
  - Basic logging
  - Debug mode
  - File logging
  - Different levels for console/file
  - Validation error logging
  - Runtime level changes
  - Custom formats
  - Silent mode

## Usage Examples

### Basic Usage
```python
import python_magnetgeo as pmg

# Configure logging (optional - uses INFO by default)
pmg.configure_logging(level='INFO')

# Use the package normally - operations will be logged
helix = pmg.Helix(name="H1", r=[10, 20], z=[0, 50])
helix.dump()
```

### Debug Mode
```python
import python_magnetgeo as pmg

# Enable detailed logging
pmg.configure_logging(level='DEBUG')

# See detailed information about all operations
obj = pmg.load("data/config.yaml")
```

### Log to File
```python
import python_magnetgeo as pmg

# Log to both console and file
pmg.configure_logging(
    level='INFO',
    log_file='magnetgeo.log'
)
```

### Different Levels
```python
import python_magnetgeo as pmg

# Show only warnings on console, but log everything to file
pmg.configure_logging(
    console_level='WARNING',
    file_level='DEBUG',
    log_file='debug.log'
)
```

## What Gets Logged

### INFO Level
- Successful file loads/writes
- Major operations completion

### DEBUG Level
- File loading details (paths, directories)
- Validation checks (when they pass)
- Internal state changes

### ERROR Level
- Validation failures
- File not found errors
- YAML/JSON parsing errors
- Type mismatches

## Benefits

1. **Debugging**: Easier to track down issues in complex geometries
2. **Monitoring**: See what the package is doing
3. **Production**: Log to files for later analysis
4. **Flexible**: Configure different levels for different outputs
5. **Backwards Compatible**: Logging is optional and doesn't break existing code

## Testing

The logging implementation has been tested with:
- Basic configuration tests
- File logging tests  
- Integration with existing package functionality
- Multiple log level tests
- Format customization tests

All tests pass and logging integrates seamlessly with the existing codebase.

## Files Created/Modified

### Created:
- `python_magnetgeo/logging_config.py` (262 lines)
- `docs/logging.md` (comprehensive guide)
- `examples/logging_examples.py` (demonstration script)

### Modified:
- `python_magnetgeo/__init__.py` (added logging imports/exports)
- `python_magnetgeo/utils.py` (added logging calls)
- `python_magnetgeo/base.py` (added logger import)
- `python_magnetgeo/validation.py` (added logging for validations)

## No Breaking Changes

The logging implementation:
- ✅ Doesn't change any existing APIs
- ✅ Is completely optional
- ✅ Works with existing code without modification
- ✅ Defaults to sensible behavior (INFO level to console)
- ✅ Can be completely disabled if desired

## Next Steps (Optional)

Future enhancements could include:
1. Add logging to more modules (Helix, Ring, Insert, etc.)
2. Add structured logging for better parsing
3. Add log rotation support for long-running processes
4. Add performance logging (timing information)
5. Integration with external logging systems (syslog, etc.)

## Conclusion

Logging support has been successfully added to python_magnetgeo, providing developers and users with powerful tools to understand, debug, and monitor geometry processing operations. The implementation is flexible, well-documented, and ready for immediate use.
