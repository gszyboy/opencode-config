---
name: sequential-thinking
description: 使用 Sequential Thinking MCP 进行结构化、逐步的问题分解与推理。当需要将复杂问题分解为可管理步骤、多步骤推理、算法设计、架构规划、调试分析、假设验证、迭代探索时必须使用。
tools: [sequentialthinking]
---

# Sequential Thinking MCP 使用规范

## 核心概念

Sequential Thinking 让你能够：
- **分解复杂问题**：将问题拆分为有序的思考步骤
- **迭代修正**：基于新信息修订之前的思考
- **分支探索**：探索替代推理路径
- **动态调整**：根据需要增加或减少思考步骤

## 触发条件

在评估任务复杂度后立即调用 `sequentialthinking` 工具：

| 场景 | 典型任务 | 预估步骤 |
|------|----------|----------|
| 复杂分析 | 多步骤推理、因果分析 | 5-10 步 |
| 规划任务 | 系统设计、架构规划 | 4-8 步 |
| 调试排查 | 根因定位、bug 分析 | 5-7 步 |
| 数学/逻辑 | 推导、证明、决策树 | 6-10 步 |
| 探索性任务 | 问题边界不清晰 | 动态调整 |

---

## 工具参数详解

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `thought` | string | ✅ | 当前思考步骤内容 |
| `thoughtNumber` | integer | ✅ | 当前思考编号（从 1 开始） |
| `totalThoughts` | integer | ✅ | 预估总思考数（可动态调整） |
| `nextThoughtNeeded` | boolean | ✅ | 是否需要下一个思考步骤 |
| `isRevision` | boolean | ❌ | 是否是对之前思考的修订 |
| `revisesThought` | integer | ❌ | 正在修订的思考编号 |
| `branchFromThought` | integer | ❌ | 分支起点思考编号 |
| `branchId` | string | ❌ | 分支标识符 |
| `needsMoreThoughts` | boolean | ❌ | 是否需要更多思考步骤 |

---

## 标准工作流

```
步骤 1: 初始分析 → 生成初步假设/理解问题
步骤 2: 深入分解 → 识别关键要素和约束
步骤 3-N: 逐步推理 → 验证、修正、完善
最后一步: 总结结论 → 验证假设、给出方案
```

---

## 调用模式

### 模式 1: 线性推理（逐步深入）

**步骤 1 - 初始分析：**
```json
{
  "thought": "首先理解问题的核心约束：输入是xxx，目标是xxx，关键限制是xxx。初步判断可以采用xxx方法。",
  "thoughtNumber": 1,
  "totalThoughts": 5,
  "nextThoughtNeeded": true
}
```

**步骤 2 - 深入分解：**
```json
{
  "thought": "将问题分解为：1) xxx；2) xxx；3) xxx。其中最关键的是xxx，因为xxx。",
  "thoughtNumber": 2,
  "totalThoughts": 5,
  "nextThoughtNeeded": true
}
```

**步骤 N - 最终结论：**
```json
{
  "thought": "结论：基于以上分析，方案xxx是最优选择。优点：xxx。需要注意：xxx。",
  "thoughtNumber": 5,
  "totalThoughts": 5,
  "nextThoughtNeeded": false
}
```

### 模式 2: 修订思考

当发现之前推理有误或需要优化时：
```json
{
  "thought": "重新审视思考N：之前认为xxx，但实际上xxx。因此修正为xxx。",
  "thoughtNumber": 4,
  "totalThoughts": 6,
  "nextThoughtNeeded": true,
  "isRevision": true,
  "revisesThought": 2
}
```

### 模式 3: 分支探索

当需要探索多种方案时：
```json
{
  "thought": "方案B（替代路径）：不同于方案A的xxx，这里采用xxx思路。",
  "thoughtNumber": 4,
  "totalThoughts": 6,
  "nextThoughtNeeded": true,
  "branchFromThought": 2,
  "branchId": "方案B-xxx"
}
```

---

## 常见场景示例

### 场景 1: 算法设计

**任务**："设计一个 LRU 缓存，支持 get 和 put 操作，均要求 O(1) 时间复杂度"

```
1. 理解需求 → O(1) get/put → 需要哈希表
2. 维护访问顺序 → 需要链表
3. 组合方案 → 哈希表 + 双向链表
4. 设计节点结构
5. 实现 get 操作
6. 实现 put 操作
7. 处理边界情况
8. 验证时间复杂度
```

### 场景 2: Bug 调试

**任务**："这个 API 调用在生产环境偶发性失败，本地无法复现"

```
1. 收集症状 → 偶发性、无规律、本地正常
2. 列出可能原因 → 超时、网络、并发、缓存
3. 逐一排查 → 优先级排序
4. 定位根因 → 最大概率原因
5. 设计验证方案
6. 给出修复建议
```

### 场景 3: 架构决策

**任务**："团队 10 人，项目周期 6 个月，应该用微服务还是单体"

```
1. 分析项目特征 → 规模、复杂度、团队经验
2. 列出决策因素 → 部署复杂度、团队协作、技术债务
3. 评估各方案利弊
4. 权衡关键权衡点
5. 给出分阶段建议
```

---

## 最佳实践

### 思考内容编写

- **具体明确**：包含具体的分析、代码、公式，而非泛泛描述
- **逻辑连贯**：后续思考基于之前结果，形成推理链条
- **适时总结**：在关键节点总结进展和下一步方向

### 动态调整

| 情况 | 操作 |
|------|------|
| 发现问题比预期复杂 | `needsMoreThoughts: true`，或增加 `totalThoughts` |
| 问题比预期简单 | 减少 `totalThoughts`，提前设置 `nextThoughtNeeded: false` |
| 需要探索新方向 | 使用分支，`branchFromThought` 指定起点 |

### 修订 vs 分支

| 类型 | 适用场景 |
|------|----------|
| **修订** | 发现错误、需要完善、方案优化 |
| **分支** | 探索不同方案、并行思考、方案对比 |

### 结束条件

设置 `nextThoughtNeeded: false` 当：
1. ✅ 已形成清晰的解决方案
2. ✅ 假设已验证或否定
3. ✅ 问题已完全分解并解决

---

## 注意事项

1. **避免过度使用**：简单任务（如单行修改）不需要结构化思考
2. **保持思考质量**：每步应有实质内容，避免无意义填充
3. **参数语义正确**：revision 必须配合 `revisesThought`
4. **主动触发**：评估后主动开始，无需等待用户明确要求
