---
name: dev-progress
description: 管理开发进度状态，使用 progress.json 记录任务进度，支持会话恢复
agent: build
---

# 开发进度管理

使用 `docs/progress.json` 管理开发进度，支持会话中断/压缩后恢复。

## progress.json 结构

```json
{
  "project": "项目名称",
  "version": "1.0",
  "lastUpdated": "2026-03-22T10:00:00Z",
  "currentPhase": 1,
  "phases": {
    "1": {
      "name": "MVP",
      "status": "active",
      "tasks": [
        {
          "id": 1,
          "title": "任务名称",
          "description": "任务描述",
          "status": "completed",
          "createdAt": "2026-03-22T10:00:00Z",
          "startedAt": "2026-03-22T10:05:00Z",
          "completedAt": "2026-03-22T11:30:00Z",
          "files": ["file1.ts", "file2.ts"]
        },
        {
          "id": 2,
          "title": "当前任务",
          "status": "in_progress",
          "startedAt": "2026-03-22T14:00:00Z"
        }
      ]
    }
  },
  "metadata": {
    "totalTasks": 5,
    "completedTasks": 1,
    "inProgressTasks": 1,
    "pendingTasks": 3
  }
}
```

## 任务状态

| 状态 | 说明 |
|------|------|
| `pending` | 待开始 |
| `in_progress` | 进行中 |
| `completed` | 已完成 |
| `blocked` | 被阻塞 |

## 操作规则

### 读取进度

执行任务前，必须先读取 `docs/progress.json`：
1. 找到 `status: "in_progress"` 的任务作为当前任务
2. 如果没有进行中的任务，从 `pending` 任务中取第一个
3. 如果所有任务都已完成，提示用户

### 更新进度

任务完成后，更新 progress.json：

1. 将当前任务 `status` 改为 `"completed"`
2. 设置 `completedAt` 为完成时间
3. 记录 `files` 为修改的文件列表
4. 从 `pending` 任务中取第一个，设置为 `in_progress`
5. 更新 `lastUpdated` 时间戳
6. 更新 `metadata` 统计

### 初始化进度

第一次使用 `/dev` 时，如果 `docs/progress.json` 不存在，从 `docs/development-plan.md` 生成。

模板参考：`~/.config/opencode/skills/dev-progress/progress-template.json`

## 时间戳格式

使用 ISO 8601 格式：`2026-03-22T14:00:00Z`

## 注意事项

1. **保持 JSON 格式正确**：使用 jq 或手动校验
2. **原子更新**：读取 → 修改 → 写入，避免并发问题
3. **保留历史**：notes 字段记录重要信息
