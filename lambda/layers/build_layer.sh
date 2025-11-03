#!/bin/bash
# Build Lambda layer for common dependencies

set -e

LAYER_DIR="common"
PYTHON_DIR="${LAYER_DIR}/python"

echo "Building Lambda layer: ${LAYER_DIR}"

# Clean previous build
rm -rf ${LAYER_DIR}/python

# Create Python directory
mkdir -p ${PYTHON_DIR}

# Install dependencies to python directory
pip install -r ${LAYER_DIR}/requirements.txt -t ${PYTHON_DIR}

# Remove unnecessary files to reduce layer size
find ${PYTHON_DIR} -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find ${PYTHON_DIR} -type f -name "*.pyc" -delete
find ${PYTHON_DIR} -type f -name "*.pyo" -delete

# Remove test files
find ${PYTHON_DIR} -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true
find ${PYTHON_DIR} -type d -name "test" -exec rm -rf {} + 2>/dev/null || true
find ${PYTHON_DIR} -name "test_*.py" -delete
find ${PYTHON_DIR} -name "*_test.py" -delete

# Remove documentation
find ${PYTHON_DIR} -name "*.md" -delete
find ${PYTHON_DIR} -name "LICENSE" -delete
find ${PYTHON_DIR} -name "*.txt" -not -name "sitecustomize.py" -delete

echo "✅ Lambda layer built successfully"
echo "Size: $(du -sh ${LAYER_DIR}/python | cut -f1)"

