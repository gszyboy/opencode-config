# 通用开发规范

> 本文档补充 AGENTS.md 中未覆盖的通用规范。
> 基础约束（Change Budget、设计原则、安全规范、开发节奏、决策升级机制）请参见主文档：@~/.config/opencode/AGENTS.md

---

## Git 提交规范

### 提交信息格式

```
<类型>: <简短描述>

[可选的详细说明]
```

### 提交类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat: 添加用户登录功能` |
| `fix` | Bug 修复 | `fix: 修复登录页面样式错位` |
| `docs` | 文档更新 | `docs: 更新 README` |
| `style` | 代码格式（不影响功能） | `style: 格式化代码` |
| `refactor` | 重构（不是新功能或修复） | `refactor: 简化 API 调用逻辑` |
| `perf` | 性能优化 | `perf: 优化列表渲染速度` |
| `test` | 测试相关 | `test: 添加用户模块单元测试` |
| `chore` | 构建/工具相关 | `chore: 更新依赖版本` |
| `hotfix` | 紧急修复 | `hotfix: 修复支付接口崩溃` |

### 规则

1. **标题简短**：不超过 50 个字符
2. **使用祈使句**："添加"而非"已添加"
3. **不加句号**：标题结尾不加标点
4. **关联 Issue**：有 Issue 时加上 `#123`
5. **一次一提交**：一个提交只做一件事

### 示例

```
# 好
feat: 添加用户注册功能
fix: 修复商品列表分页问题
docs: 更新 API 文档

# 不好
修改了一些东西
修复了 bug
添加了新功能还有优化了代码
```

### 分支命名规范

```
<类型>/<简短描述>
feature/user-login
fix/payment-bug
hotfix/security-patch
```

### Git 操作流程

```bash
# 1. 开始新任务前先拉取最新代码
git pull origin main

# 2. 创建分支
git checkout -b feature/user-login

# 3. 开发完成后提交
git add .
git commit -m "feat: 添加用户登录功能"

# 4. 推送并创建 PR/MR
git push -u origin feature/user-login
```

### 提交前检查

- [ ] 代码能正常运行
- [ ] 没有 console.log/调试代码
- [ ] 没有硬编码的密钥或密码
- [ ] 提交信息符合规范
- [ ] 只提交相关的改动

---

## 代码审查规范

### 作为提交者的责任
1. 提交前自己先 review 一遍代码
2. 确保代码符合项目规范
3. 提交信息清晰描述改动内容

### Commit Message 模板（可选）

在项目根目录创建 `.gitmessage.txt`：

```
# <类型>: <简短描述>
#
# 正文描述（可选）
#
# 类型: feat | fix | docs | style | refactor | perf | test | chore | hotfix
# 关联: Closes #123
```
