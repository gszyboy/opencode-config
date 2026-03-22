---
description: 开始一个新的开发任务，自动读取和更新进度
agent: build
---

## 任务：$ARGUMENTS

## 第一步：读取进度

首先读取 `docs/progress.json` 了解当前状态：

1. 找到 `status: "in_progress"` 的任务作为当前任务
2. 如果没有进行中的任务，从 `pending` 任务中取第一个
3. 如果所有任务都已完成，提示用户
4. 如果 progress.json 不存在，从 `docs/development-plan.md` 生成

## 第二步：确认任务

根据读取的进度，确认当前任务：

- **当前任务**：[任务名称]
- **阶段**：[阶段名称]
- **任务描述**：[描述]

## 第三步：执行开发

### Change Budget（强制）
- 修改文件数：≤ 3
- 修改行数：≤ 80
- 不引入新依赖
- 不修改任务范围之外的文件
- 不创建新目录（除非确实需要）
- 不重构未涉及的文件

### 开发原则
1. 简单优先，不提前抽象
2. 先让功能跑起来，再优化
3. 只有代码重复 3 次以上才抽取公共部分

### 流程
1. 确认任务范围
2. 如果涉及后端，先确认 API 结构
3. 实现
4. 简单验证

## 第四步：如果 AI 想做更多

如果 AI 说"我顺便..."、"我优化了..."、"我重构了..."，立即：
1. /undo 撤销
2. 只做任务要求的事

## 第五步：完成后更新进度

任务完成后，更新 `docs/progress.json`：

1. 将当前任务 `status` 改为 `"completed"`
2. 设置 `completedAt` 为完成时间（ISO 8601 格式：`2026-03-22T14:00:00Z`）
3. 记录 `files` 为修改的文件列表
4. 从 `pending` 任务中取第一个，设置为 `in_progress`
5. 更新 `lastUpdated` 时间戳
6. 更新 `metadata` 统计

### 更新示例

```json
{
  "lastUpdated": "2026-03-22T15:30:00Z",
  "phases": {
    "1": {
      "tasks": [
        {
          "id": 1,
          "status": "completed",
          "completedAt": "2026-03-22T15:30:00Z",
          "files": ["src/api/user.ts", "src/views/Login.vue"]
        },
        {
          "id": 2,
          "status": "in_progress",
          "startedAt": "2026-03-22T15:30:00Z"
        }
      ]
    }
  }
}
```

## 完成后

1. 列出修改的文件
2. 确认在 Change Budget 范围内
3. 说明功能是否验证通过
4. 确认 progress.json 已更新
