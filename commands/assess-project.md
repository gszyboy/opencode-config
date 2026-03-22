---
description: 评估已有项目，确定AI介入策略和风险点
agent: plan
---

@~/.config/opencode/skills/existing-project-assessor/SKILL.md

请执行项目评估流程：

## 评估流程

### 1. 结构扫描
```bash
# 扫描项目结构
glob **/*.py **/requirements.txt 2>/dev/null | head -20
glob **/*.js **/*.ts package.json 2>/dev/null | head -20
glob composer.json **/*.php 2>/dev/null | head -10
glob **/*.vue 2>/dev/null | head -20
```

### 2. 技术栈识别
根据文件特征判断技术栈（Python/JavaScript/PHP等）和框架（FastAPI/Vue/ThinkPHP等）

### 3. 风险评估
评估维度：代码规模、测试覆盖、技术债务、依赖复杂度

### 4. 核心识别
识别红线区域（不改）和可改区域

## 输出格式

生成项目评估报告：
```
# 项目评估报告

## 基本信息
- 项目类型：[自研/二次开发/开源改造]
- 技术栈：[列出]
- 代码规模：[行数估算]

## 风险矩阵
| 区域 | 风险 | 说明 |

## 推荐级别：L[X]

## 红线清单
1. ...

## 可改区域
1. ...

## 技术债务优先级
| 优先级 | 问题 | 影响 |

## 下一步建议
...
```

## 约束
- 只读操作，不改任何文件
- 遇到不确定的文件先询问
- 保守评估，宁可多问
