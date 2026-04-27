#!/bin/bash
CONFIG_DIR="$HOME/.config/opencode"
CURRENT="$CONFIG_DIR/oh-my-openagent.json"
NORMAL="$CONFIG_DIR/oh-my-openagent.json.正常版"
EMERGENCY="$CONFIG_DIR/oh-my-openagent.json.应急版"
DEEPSEEK="$CONFIG_DIR/oh-my-openagent.json.DeepSeek版"

usage() {
    echo "用法: $0 [normal|emergency|deepseek|current]"
    echo ""
    echo "  normal     → 使用正常版（prometheus/sisyphus 走 kimi）"
    echo "  emergency  → 使用应急版（prometheus/sisyphus 走 MiniMax-M2.7）"
    echo "  deepseek   → 使用 DeepSeek 版（主模型为 deepseek-v4-pro）"
    echo "  current    → 查看当前配置"
    echo ""
    echo "当前状态:"
    diff -q "$CURRENT" "$NORMAL" &>/dev/null && echo "  ✅ 当前是正常版" || true
    diff -q "$CURRENT" "$EMERGENCY" &>/dev/null && echo "  ✅ 当前是应急版" || true
    diff -q "$CURRENT" "$DEEPSEEK" &>/dev/null && echo "  ✅ 当前是 DeepSeek 版" || true
    if ! diff -q "$CURRENT" "$NORMAL" &>/dev/null && ! diff -q "$CURRENT" "$EMERGENCY" &>/dev/null && ! diff -q "$CURRENT" "$DEEPSEEK" &>/dev/null; then
        echo "  ⚠️  当前既不是正常版也不是应急版也不是 DeepSeek 版"
    fi
    exit 1
}

case "$1" in
    normal)
        cp "$NORMAL" "$CURRENT"
        echo "已切换到正常版"
        ;;
    emergency)
        cp "$EMERGENCY" "$CURRENT"
        echo "已切换到应急版"
        ;;
    deepseek)
        cp "$DEEPSEEK" "$CURRENT"
        echo "已切换到 DeepSeek 版"
        ;;
    current)
        diff -q "$CURRENT" "$NORMAL" &>/dev/null && echo "当前: 正常版" || true
        diff -q "$CURRENT" "$EMERGENCY" &>/dev/null && echo "当前: 应急版" || true
        diff -q "$CURRENT" "$DEEPSEEK" &>/dev/null && echo "当前: DeepSeek 版" || true
        if ! diff -q "$CURRENT" "$NORMAL" &>/dev/null && ! diff -q "$CURRENT" "$EMERGENCY" &>/dev/null && ! diff -q "$CURRENT" "$DEEPSEEK" &>/dev/null; then
            echo "当前: 未识别版本（既不是正常版也不是应急版也不是 DeepSeek 版）"
        fi
        ;;
    *)
        usage
        ;;
esac