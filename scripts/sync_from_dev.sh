#!/bin/bash

# Sync From Development Repository Script
# This script syncs production-ready code from dev repo to release repo

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================"
echo "Cardiac AI-CAC Release Sync Script"
echo "========================================${NC}"
echo

# Configuration
DEV_REPO_PATH="${DEV_REPO_PATH:-$HOME/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research}"
RELEASE_REPO_PATH="${RELEASE_REPO_PATH:-$(pwd)}"

echo -e "${YELLOW}Configuration:${NC}"
echo "Dev Repo:     $DEV_REPO_PATH"
echo "Release Repo: $RELEASE_REPO_PATH"
echo

# Verify paths
if [ ! -d "$DEV_REPO_PATH" ]; then
    echo -e "${RED}ERROR: Dev repo not found at $DEV_REPO_PATH${NC}"
    echo "Set DEV_REPO_PATH environment variable or edit this script"
    exit 1
fi

if [ ! -d "$RELEASE_REPO_PATH/.git" ]; then
    echo -e "${RED}ERROR: Release repo not found at $RELEASE_REPO_PATH${NC}"
    exit 1
fi

# Ask for version
read -p "Enter version to sync (e.g., v1.1.4): " VERSION
if [ -z "$VERSION" ]; then
    echo -e "${RED}ERROR: Version is required${NC}"
    exit 1
fi

echo
echo -e "${GREEN}[1/6] Creating clean export directory...${NC}"
EXPORT_DIR="/tmp/cardiac-ai-cac-export-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$EXPORT_DIR"
echo "Export dir: $EXPORT_DIR"

echo
echo -e "${GREEN}[2/6] Exporting source code from dev repo...${NC}"

# Create src directory structure
mkdir -p "$EXPORT_DIR/src"

# Export cardiac_calcium_scoring module
echo "  - Exporting cardiac_calcium_scoring..."
mkdir -p "$EXPORT_DIR/src/cardiac_calcium_scoring"
rsync -av \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='*.log' \
    --exclude='test_*' \
    --exclude='output/' \
    --exclude='logs/' \
    --exclude='dist/' \
    --exclude='.git' \
    --exclude='*.egg-info' \
    "$DEV_REPO_PATH/tools/cardiac_calcium_scoring/" \
    "$EXPORT_DIR/src/cardiac_calcium_scoring/"

# Export shared modules
echo "  - Exporting shared modules..."
mkdir -p "$EXPORT_DIR/src/shared"
rsync -av \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='test_*' \
    --exclude='.git' \
    "$DEV_REPO_PATH/shared/" \
    "$EXPORT_DIR/src/shared/"

echo
echo -e "${GREEN}[3/6] Exporting requirements files...${NC}"
mkdir -p "$EXPORT_DIR/requirements"
cp "$DEV_REPO_PATH/tools/cardiac_calcium_scoring/deployment/requirements"*.txt \
   "$EXPORT_DIR/requirements/" 2>/dev/null || \
cp "$DEV_REPO_PATH/requirements"*.txt \
   "$EXPORT_DIR/requirements/" 2>/dev/null || \
echo "  WARNING: No requirements files found in dev repo"

echo
echo -e "${GREEN}[4/6] Cleaning up export...${NC}"
# Remove any remaining test files
find "$EXPORT_DIR" -type f -name "test_*.py" -delete
find "$EXPORT_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$EXPORT_DIR" -type f -name "*.pyc" -delete

# Count files
FILE_COUNT=$(find "$EXPORT_DIR" -type f | wc -l)
echo "  Exported $FILE_COUNT files"

echo
echo -e "${GREEN}[5/6] Syncing to release repo...${NC}"
# Copy to release repo
mkdir -p "$RELEASE_REPO_PATH/src"
cp -r "$EXPORT_DIR/src/"* "$RELEASE_REPO_PATH/src/"

mkdir -p "$RELEASE_REPO_PATH/requirements"
cp -r "$EXPORT_DIR/requirements/"* "$RELEASE_REPO_PATH/requirements/" 2>/dev/null || true

echo
echo -e "${GREEN}[6/6] Updating CHANGELOG...${NC}"
# Check if CHANGELOG needs updating
if ! grep -q "## \[$VERSION\]" "$RELEASE_REPO_PATH/CHANGELOG.md"; then
    echo -e "${YELLOW}WARNING: CHANGELOG.md does not contain version $VERSION${NC}"
    echo "Please update CHANGELOG.md before committing"
fi

echo
echo -e "${BLUE}========================================"
echo -e "${GREEN}Sync Complete!${NC}"
echo "========================================${NC}"
echo
echo "Next steps:"
echo "  1. Review changes:    cd $RELEASE_REPO_PATH && git status"
echo "  2. Update CHANGELOG:  edit CHANGELOG.md"
echo "  3. Commit changes:    git add . && git commit -m 'Sync $VERSION from dev repo'"
echo "  4. Create tag:        git tag $VERSION"
echo "  5. Push:              git push origin main && git push origin $VERSION"
echo
echo "Clean up export: rm -rf $EXPORT_DIR"
echo
