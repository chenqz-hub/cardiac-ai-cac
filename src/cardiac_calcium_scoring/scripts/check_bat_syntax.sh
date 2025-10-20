#!/bin/bash
# 批处理文件语法检查工具
# 检查常见的批处理语法问题

BAT_DIR="${1:-.}"
ERRORS=0

echo "=========================================="
echo "Batch File Syntax Checker"
echo "=========================================="
echo ""

# 查找所有.bat文件
BAT_FILES=$(find "$BAT_DIR" -name "*.bat" -type f)

if [ -z "$BAT_FILES" ]; then
    echo "No .bat files found in $BAT_DIR"
    exit 0
fi

echo "Checking batch files in: $BAT_DIR"
echo ""

for BAT_FILE in $BAT_FILES; do
    echo "Checking: $BAT_FILE"
    FILE_ERRORS=0

    # 检查1: if块中未转义的特殊字符
    # 查找 if ... ( 和 ) else ( 之间的内容
    IN_IF_BLOCK=false
    LINE_NUM=0

    while IFS= read -r line; do
        ((LINE_NUM++))

        # 检测进入if块
        if echo "$line" | grep -qE '^\s*if\s+.*\($'; then
            IN_IF_BLOCK=true
        fi

        # 检测退出if块
        if echo "$line" | grep -qE '^\s*\)\s*$' && [ "$IN_IF_BLOCK" = true ]; then
            IN_IF_BLOCK=false
        fi

        # 在if块中检查问题
        if [ "$IN_IF_BLOCK" = true ]; then
            # 检查echo行中未转义的特殊字符
            if echo "$line" | grep -qE '^\s*echo\s+'; then
                # 检查未转义的 - (开头的连字符)
                if echo "$line" | grep -qE 'echo\s+.*\s-\s' && ! echo "$line" | grep -qE '\^-'; then
                    echo "  ✗ Line $LINE_NUM: Unescaped hyphen '-' in echo"
                    echo "    $line"
                    ((FILE_ERRORS++))
                fi

                # 检查未转义的括号 (但排除已转义的)
                if echo "$line" | grep -qE 'echo.*\(' && ! echo "$line" | grep -qE '\^\('; then
                    # 检查是否是变量引用 %var%
                    if ! echo "$line" | grep -qE '%[^%]+%'; then
                        echo "  ✗ Line $LINE_NUM: Unescaped parenthesis '(' in echo"
                        echo "    $line"
                        ((FILE_ERRORS++))
                    fi
                fi
            fi
        fi
    done < "$BAT_FILE"

    # 检查2: heredoc残留
    if grep -qE '^(EOF|STARTEOF|EOFSTART)' "$BAT_FILE"; then
        echo "  ✗ Found heredoc marker (EOF/STARTEOF) in file"
        ((FILE_ERRORS++))
    fi

    # 检查3: 未替换的bash变量
    if grep -qE '\$\{[A-Z_]+\}' "$BAT_FILE"; then
        echo "  ✗ Found bash variable syntax \${VAR}"
        grep -n '\$\{[A-Z_]+\}' "$BAT_FILE" | head -3
        ((FILE_ERRORS++))
    fi

    # 检查4: 引号不匹配
    QUOTE_COUNT=$(grep -o '"' "$BAT_FILE" | wc -l)
    if [ $((QUOTE_COUNT % 2)) -ne 0 ]; then
        echo "  ⚠ Warning: Odd number of quotes ($QUOTE_COUNT)"
    fi

    if [ $FILE_ERRORS -eq 0 ]; then
        echo "  ✓ No obvious errors found"
    else
        echo "  ✗ Found $FILE_ERRORS potential issues"
        ((ERRORS += FILE_ERRORS))
    fi
    echo ""
done

echo "=========================================="
if [ $ERRORS -eq 0 ]; then
    echo "✓ All checks passed!"
    exit 0
else
    echo "✗ Found $ERRORS potential issues"
    echo ""
    echo "Note: This is a basic syntax checker."
    echo "Please test on actual Windows system to confirm."
    exit 1
fi
