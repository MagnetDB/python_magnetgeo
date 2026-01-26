#!/bin/bash
# Build script for Singularity container

set -e

# Configuration
IMAGE_NAME="python_magnetgeo.sif"
DEF_FILE="Singularity.def"

# Check if singularity/apptainer is installed
if command -v singularity &> /dev/null; then
    CONTAINER_CMD="singularity"
elif command -v apptainer &> /dev/null; then
    CONTAINER_CMD="apptainer"
else
    echo "Error: Neither singularity nor apptainer found in PATH"
    echo "Please install Singularity/Apptainer first:"
    echo "  https://apptainer.org/docs/admin/main/installation.html"
    exit 1
fi

echo "Using: $CONTAINER_CMD"
echo "Building Singularity container: $IMAGE_NAME"
echo "From definition file: $DEF_FILE"
echo ""

# Build the container
# Note: This requires sudo/root privileges or fakeroot
if [ "$EUID" -eq 0 ] || [ -n "$SINGULARITY_FAKEROOT" ]; then
    $CONTAINER_CMD build "$IMAGE_NAME" "$DEF_FILE"
else
    echo "Building with sudo (requires root privileges)..."
    echo "Alternatively, you can use --fakeroot if configured:"
    echo "  $CONTAINER_CMD build --fakeroot $IMAGE_NAME $DEF_FILE"
    echo ""
    sudo $CONTAINER_CMD build "$IMAGE_NAME" "$DEF_FILE"
fi

# Test the container
if [ -f "$IMAGE_NAME" ]; then
    echo ""
    echo "Container built successfully!"
    echo ""
    echo "Testing container..."
    $CONTAINER_CMD exec "$IMAGE_NAME" python -c "import python_magnetgeo; print('✓ python_magnetgeo imported successfully')"

    echo ""
    echo "Build complete! You can now use the container with:"
    echo "  $CONTAINER_CMD shell $IMAGE_NAME"
    echo "  $CONTAINER_CMD exec $IMAGE_NAME python your_script.py"
    echo "  $CONTAINER_CMD run $IMAGE_NAME -c 'import python_magnetgeo'"
else
    echo "Error: Container build failed"
    exit 1
fi
