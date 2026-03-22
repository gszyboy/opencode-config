/**
 * Auto Backup Reminder Plugin
 * 
 * 在修改核心文件前自动提醒备份
 */

const CORE_PATTERNS = [
  'models/',
  'schemas/',
  'auth/',
  'payment/',
  'order/',
  'core/',
  'main.py',
  'database.py',
  'config.py',
  'App.vue',
  'main.ts',
  'index.tsx'
]

const BACKUP_COMMANDS = [
  'git tag "backup/before-change-$(date +%Y%m%d-%H%M%S)"'
]

export default async (ctx) => ({
  'tool.execute.before': async (input) => {
    const tool = input.tool
    
    // 只在写操作前检查
    if (tool === 'write' || tool === 'edit') {
      const filePath = input.args?.filePath || ''
      const isCoreFile = CORE_PATTERNS.some(p => filePath.includes(p))
      
      if (isCoreFile) {
        console.log(`
┌─────────────────────────────────────────────────────────┐
│  ⚠️  即将修改核心文件                                    │
├─────────────────────────────────────────────────────────┤
│  文件: ${filePath.padEnd(45)} │
│                                                          │
│  建议先备份:                                             │
│  ${BACKUP_COMMANDS[0].padEnd(49)} │
│                                                          │
│  或使用 /undo 撤销更改                                   │
└─────────────────────────────────────────────────────────┘
`)
      }
    }
  },

  'tool.execute.after': async (input, output) => {
    const tool = input.tool
    
    if (tool === 'bash') {
      const command = input.args?.command || ''
      
      // git 操作后提醒
      if (command.includes('git commit') && !command.includes('--no-verify')) {
        console.log(`
📦 提交成功！
   建议: git push 同步到远程仓库
   或使用 git log 查看提交历史
`)
      }
    }
  }
})
