# Singularity Container for Python Magnet Geometry

This directory contains the Singularity/Apptainer definition file for creating a containerized environment for the Python Magnet Geometry package.

## Files

- `Singularity.def` - Singularity definition file
- `build-singularity.sh` - Build script for creating the container

## Prerequisites

You need to have Singularity or Apptainer installed on your system:

- **Apptainer** (recommended): https://apptainer.org/docs/admin/main/installation.html
- **Singularity**: https://sylabs.io/singularity/

## Building the Container

### Quick Build

```bash
./build-singularity.sh
```

### Manual Build

With sudo privileges:
```bash
sudo singularity build python_magnetgeo.sif Singularity.def
```

Or with fakeroot (if configured):
```bash
singularity build --fakeroot python_magnetgeo.sif Singularity.def
```

Or using Apptainer:
```bash
apptainer build python_magnetgeo.sif Singularity.def
```

## Using the Container

### Interactive Shell

Open an interactive shell in the container:
```bash
singularity shell python_magnetgeo.sif
# or
apptainer shell python_magnetgeo.sif
```

### Execute Commands

Run a Python script:
```bash
singularity exec python_magnetgeo.sif python your_script.py
```

Run Python code directly:
```bash
singularity exec python_magnetgeo.sif python -c "import python_magnetgeo; print('Hello from container')"
```

### Run with Default Runscript

```bash
singularity run python_magnetgeo.sif -c "import python_magnetgeo"
```

### Bind Mount Directories

To access files from your host system:
```bash
singularity exec --bind /path/to/data:/data python_magnetgeo.sif python script.py
```

Example with the data directory:
```bash
singularity exec --bind $(pwd)/data:/data python_magnetgeo.sif python -c "import yaml; print(yaml.safe_load(open('/data/HL-31_H1.yaml')))"
```

### Running Tests

The container includes pytest and testing dependencies. Run tests with:
```bash
singularity exec python_magnetgeo.sif python -m pytest -v
```

> **Note**: Tests are automatically run during the container build process in the `%test` section to verify the installation.

## Container Details

- **Base Image**: Ubuntu 22.04
- **Python Version**: 3.11
- **Main Dependencies**:
  - pyyaml >= 6.0
  - pandas >= 1.5.3
  - pytest >= 8.2.0 (for testing)

## Customization

You can customize the container by editing `Singularity.def`:

1. **Change Python version**: Modify the `python3.11` package in the `%post` section
2. **Add dependencies**: Add packages to the pip install commands
3. **Include additional system tools**: Add packages to the apt-get install command
4. **Add data files**: Use the `%files` section to copy files into the container

## Examples

### Example 1: Load YAML Configuration

```bash
singularity exec --bind $(pwd)/data:/data python_magnetgeo.sif python << 'EOF'
import yaml
with open('/data/HL-31_H1.yaml', 'r') as f:
    config = yaml.safe_load(f)
    print(f"Loaded configuration: {config.get('name', 'Unknown')}")
EOF
```

### Example 2: Run Tests

```bash
singularity exec python_magnetgeo.sif python -m pytest -v
```

Run specific test files or markers:
```bash
singularity exec python_magnetgeo.sif python -m pytest -v -k "test_profile"
singularity exec python_magnetgeo.sif python -m pytest -v -m "unit"
```

### Example 3: Interactive Development

```bash
singularity shell --bind $(pwd):/workspace --pwd /workspace python_magnetgeo.sif
# Now you're in the container with your current directory mounted
python your_development_script.py
```

## HPC Usage

### On a SLURM Cluster

Create a job script `job.sh`:
```bash
#!/bin/bash
#SBATCH --job-name=magnetgeo
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=01:00:00

module load singularity  # if available

singularity exec python_magnetgeo.sif python simulation.py
```

Submit the job:
```bash
sbatch job.sh
```

## Troubleshooting

### Permission Issues

If you get permission errors when building:
- Use `sudo` for building
- Configure fakeroot: https://apptainer.org/docs/admin/main/user_namespace.html

### Module Import Errors

If python_magnetgeo cannot be imported:
```bash
singularity exec python_magnetgeo.sif python -c "import sys; print(sys.path)"
```

Check that `/opt/python_magnetgeo` is in the Python path.

### GPU Support

To use NVIDIA GPUs in the container:
```bash
singularity exec --nv python_magnetgeo.sif python gpu_script.py
```

## Building from GitHub

To build directly from the GitHub repository:

```bash
# Clone the repository
git clone https://github.com/MagnetDB/python_magnetgeo.git
cd python_magnetgeo

# Build the container
sudo singularity build python_magnetgeo.sif Singularity.def
```

## Support

For issues related to:
- Python Magnet Geometry package: https://github.com/MagnetDB/python_magnetgeo/issues
- Singularity/Apptainer: https://apptainer.org/help
