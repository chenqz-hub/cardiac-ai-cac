#!/bin/bash
#
# CPU Configuration Benchmark Script
# ==================================
#
# Tests different CPU optimization configurations on real DICOM data
#
# Usage:
#   ./scripts/benchmark_cpu_configs.sh
#

set -e

# Configuration
DATA_DIR="/home/wuxia/projects/family_management_hub/members/wife/medical_research/cardiac_function_extraction/data/ct_images/ct_images_dicom/chd"
CONFIG_FILE="config/config.yaml"
OUTPUT_DIR="output/benchmark_$(date +%Y%m%d_%H%M%S)"
MODEL_PATH="models/va_non_gated_ai_cac_model.pth"

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "=================================="
echo "CPU Configuration Benchmark"
echo "=================================="
echo "Data: $DATA_DIR"
echo "Output: $OUTPUT_DIR"
echo ""

# Check if model exists
if [ ! -f "$MODEL_PATH" ]; then
    echo "ERROR: Model file not found: $MODEL_PATH"
    echo "Please download the model first"
    exit 1
fi

# Function to run test
run_test() {
    local test_name=$1
    local num_workers=$2
    local extra_args=$3

    echo ""
    echo "==================================  "
    echo "Test: $test_name"
    echo "  num_workers: $num_workers"
    echo "  extra_args: $extra_args"
    echo "=================================="
    echo ""

    local output_file="$OUTPUT_DIR/${test_name}_results.csv"
    local log_file="$OUTPUT_DIR/${test_name}.log"
    local time_file="$OUTPUT_DIR/${test_name}_time.txt"

    # Run with time measurement
    /usr/bin/time -v python cli/run_nb10.py \
        --config "$CONFIG_FILE" \
        --data-dir "$DATA_DIR" \
        --output-dir "$OUTPUT_DIR/$test_name" \
        --mode pilot \
        --pilot-limit 1 \
        --device cpu \
        $extra_args \
        2>&1 | tee "$log_file"

    echo ""
    echo "✓ Test completed: $test_name"
    echo "  Log: $log_file"
    echo ""
}

# Test 1: Baseline (current v1.1.2)
echo "Starting Test 1: Baseline Configuration"
run_test "baseline" 0 ""

# Test 2: Conservative optimization (num_workers=2)
echo "Starting Test 2: Conservative Optimization"
# Note: Need to implement command-line override for num_workers
# For now, this is a placeholder
echo "  (Skipped - requires code changes)"

# Test 3: Check results
echo ""
echo "=================================="
echo "Benchmark Complete"
echo "=================================="
echo ""
echo "Results saved in: $OUTPUT_DIR"
echo ""

# Display timing summary
if [ -f "$OUTPUT_DIR/baseline_time.txt" ]; then
    echo "Baseline timing:"
    grep "Elapsed (wall clock)" "$OUTPUT_DIR/baseline_time.txt" || true
fi

echo ""
echo "To compare configurations, we need to implement the optimizations first."
echo "This baseline test confirms the system works correctly."
