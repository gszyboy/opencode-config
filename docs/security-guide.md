# 安全增强规范

## Plugins 列表

| 插件 | 功能 | 保护级别 |
|------|------|----------|
| `env-protection.js` | 保护 .env 等敏感文件 | 高 |
| `sensitive-files-logger.js` | 记录重要文件操作 | 中 |
| `auto-backup-reminder.js` | 修改核心文件前提醒备份 | 中 |

---

## 敏感文件保护

### 受保护的文件模式

```
.env, .env.local, .env.development, .env.production
.env.*, secrets.json, credentials.json
*.key, *.pem, id_rsa*, *.secret, passwords.json
```

### 保护行为

| 操作 | 行为 |
|------|------|
| 读取敏感文件 | ❌ 阻止 + 提示 |
| 写入敏感文件 | ❌ 阻止 + 提示 |
| 读取 .env.example | ✅ 允许 |

---

## 核心文件提醒

### 核心文件模式

```
models/, schemas/, auth/, payment/, order/
core/, main.py, database.py, config.py
App.vue, main.ts, index.tsx
```

### 提醒行为

修改核心文件前会显示：
```
⚠️  即将修改核心文件
文件: models/user.py
建议先备份: git tag "backup/before-change-..."
```

---

## 权限配置

```json
{
  "permission": {
    "edit": "ask",    // 文件编辑需要确认
    "bash": "ask"     // 命令执行需要确认
  }
}
```

### 权限说明

| 权限 | 级别 | 说明 |
|------|------|------|
| `allow` | 允许 | 自动执行，无需确认 |
| `ask` | 询问 | 执行前需要用户确认 |
| `deny` | 拒绝 | 阻止执行 |

### 规则示例

```json
"bash": {
  "*": "ask",
  "git *": "allow",
  "npm *": "allow",
  "rm *": "deny"
}
```

---

## 安全最佳实践

1. **敏感文件永不提交**
   ```bash
   # .gitignore
   .env
   *.key
   *.pem
   secrets.json
   ```

2. **使用环境变量**
   ```bash
   # 使用 {env:VAR_NAME} 语法
   apiKey: "{env:API_KEY}"
   ```

3. **定期备份**
   ```bash
   git tag "backup/$(date +%Y%m%d)"
   ```

4. **检查网络请求**
   - 禁止将密钥硬编码
   - 使用 .env.local 存储本地密钥
   - 生产环境使用 secrets manager


