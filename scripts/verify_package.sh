#!/bin/bash

# Package Verification Script
# Verifies that a release package contains all required files

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PACKAGE_DIR="${1:-.}"

echo -e "${BLUE}========================================"
echo "Package Verification Script"
echo "========================================${NC}"
echo "Checking: $PACKAGE_DIR"
echo

cd "$PACKAGE_DIR"

ERRORS=0
WARNINGS=0

# Check required directories
echo -e "${BLUE}Checking directory structure...${NC}"
REQUIRED_DIRS=(
    "src"
    "src/cardiac_calcium_scoring"
    "src/shared"
    "requirements"
    "models"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "  ${GREEN}✓${NC} $dir/"
    else
        echo -e "  ${RED}✗${NC} $dir/ (MISSING)"
        ((ERRORS++))
    fi
done

echo
echo -e "${BLUE}Checking required files...${NC}"
REQUIRED_FILES=(
    "README.md"
    "README_CN.md"
    "CHANGELOG.md"
    "requirements/requirements-cpu.txt"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "  ${GREEN}✓${NC} $file"
    else
        echo -e "  ${RED}✗${NC} $file (MISSING)"
        ((ERRORS++))
    fi
done

# Check for installation scripts
echo
echo -e "${BLUE}Checking installation scripts...${NC}"
if [ -f "install.sh" ] || [ -f "install.bat" ]; then
    [ -f "install.sh" ] && echo -e "  ${GREEN}✓${NC} install.sh" || echo -e "  ${YELLOW}○${NC} install.sh (not found)"
    [ -f "install.bat" ] && echo -e "  ${GREEN}✓${NC} install.bat" || echo -e "  ${YELLOW}○${NC} install.bat (not found)"
else
    echo -e "  ${RED}✗${NC} No installation scripts found"
    ((ERRORS++))
fi

# Check for launcher scripts
echo
echo -e "${BLUE}Checking launcher scripts...${NC}"
if [ -f "cardiac-ai-cac.sh" ] || [ -f "cardiac-ai-cac.bat" ]; then
    [ -f "cardiac-ai-cac.sh" ] && echo -e "  ${GREEN}✓${NC} cardiac-ai-cac.sh" || echo -e "  ${YELLOW}○${NC} cardiac-ai-cac.sh (not found)"
    [ -f "cardiac-ai-cac.bat" ] && echo -e "  ${GREEN}✓${NC} cardiac-ai-cac.bat" || echo -e "  ${YELLOW}○${NC} cardiac-ai-cac.bat (not found)"
else
    echo -e "  ${RED}✗${NC} No launcher scripts found"
    ((ERRORS++))
fi

# Check model file
echo
echo -e "${BLUE}Checking AI model...${NC}"
MODEL_FILE="models/va_non_gated_ai_cac_model.pth"
if [ -f "$MODEL_FILE" ]; then
    SIZE=$(du -h "$MODEL_FILE" | cut -f1)
    echo -e "  ${GREEN}✓${NC} $MODEL_FILE ($SIZE)"

    # Verify size (should be around 1.8GB)
    SIZE_BYTES=$(stat -f%z "$MODEL_FILE" 2>/dev/null || stat -c%s "$MODEL_FILE")
    if [ $SIZE_BYTES -lt 1000000000 ]; then
        echo -e "  ${YELLOW}⚠${NC}  Warning: Model file seems too small (< 1GB)"
        ((WARNINGS++))
    fi
else
    echo -e "  ${RED}✗${NC} $MODEL_FILE (MISSING)"
    ((ERRORS++))
fi

# Check dependencies
echo
echo -e "${BLUE}Checking dependencies...${NC}"
if [ -d "dependencies" ] || [ -d "wheels" ]; then
    DEP_DIR="dependencies"
    [ -d "wheels" ] && DEP_DIR="wheels"

    WHEEL_COUNT=$(find "$DEP_DIR" -name "*.whl" | wc -l)
    echo -e "  ${GREEN}✓${NC} $DEP_DIR/ ($WHEEL_COUNT wheels)"

    if [ $WHEEL_COUNT -lt 10 ]; then
        echo -e "  ${YELLOW}⚠${NC}  Warning: Only $WHEEL_COUNT wheels found (expected 30+)"
        ((WARNINGS++))
    fi
else
    echo -e "  ${YELLOW}⚠${NC}  No dependencies directory found"
    echo "     (This is OK if dependencies are downloaded during install)"
    ((WARNINGS++))
fi

# Check for Python files
echo
echo -e "${BLUE}Checking Python source code...${NC}"
PY_COUNT=$(find src -name "*.py" | wc -l)
if [ $PY_COUNT -gt 0 ]; then
    echo -e "  ${GREEN}✓${NC} Found $PY_COUNT Python files"
else
    echo -e "  ${RED}✗${NC} No Python files found in src/"
    ((ERRORS++))
fi

# Check for test files (shouldn't be present)
TEST_COUNT=$(find src -name "test_*.py" | wc -l)
if [ $TEST_COUNT -gt 0 ]; then
    echo -e "  ${YELLOW}⚠${NC}  Warning: Found $TEST_COUNT test files (should be excluded)"
    ((WARNINGS++))
fi

# Check for __pycache__ (shouldn't be present)
PYCACHE_COUNT=$(find . -type d -name "__pycache__" | wc -l)
if [ $PYCACHE_COUNT -gt 0 ]; then
    echo -e "  ${YELLOW}⚠${NC}  Warning: Found $PYCACHE_COUNT __pycache__ directories (should be cleaned)"
    ((WARNINGS++))
fi

# Check requirements file content
echo
echo -e "${BLUE}Checking requirements file...${NC}"
if [ -f "requirements/requirements-cpu.txt" ]; then
    # Check for key dependencies
    REQUIRED_PACKAGES=(
        "torch"
        "monai"
        "SimpleITK"
        "pydicom"
        "cryptography"
    )

    for pkg in "${REQUIRED_PACKAGES[@]}"; do
        if grep -qi "^$pkg" requirements/requirements-cpu.txt; then
            echo -e "  ${GREEN}✓${NC} $pkg"
        else
            echo -e "  ${RED}✗${NC} $pkg (MISSING in requirements)"
            ((ERRORS++))
        fi
    done
fi

# Check for placeholder text
echo
echo -e "${BLUE}Checking for placeholder text...${NC}"
if grep -q "USERNAME" README.md 2>/dev/null; then
    echo -e "  ${YELLOW}⚠${NC}  Warning: README.md contains 'USERNAME' placeholder"
    ((WARNINGS++))
fi

if grep -q "your-email@example.com" README.md 2>/dev/null; then
    echo -e "  ${YELLOW}⚠${NC}  Warning: README.md contains email placeholder"
    ((WARNINGS++))
fi

# Final summary
echo
echo -e "${BLUE}========================================"
echo "Verification Summary"
echo "========================================${NC}"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ Package verification PASSED${NC}"
    echo "   No errors or warnings found"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Package verification PASSED with warnings${NC}"
    echo "   Errors:   $ERRORS"
    echo "   Warnings: $WARNINGS"
    exit 0
else
    echo -e "${RED}❌ Package verification FAILED${NC}"
    echo "   Errors:   $ERRORS"
    echo "   Warnings: $WARNINGS"
    exit 1
fi
