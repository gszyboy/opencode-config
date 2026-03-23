/**
 * Auto Backup Reminder Plugin
 * 
 * 在修改核心文件前自动提醒备份
 * 测试注释 - 插件已加载
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

export const AutoBackupReminder = async ({ client }) => ({
  'tool.execute.before': async (input) => {
    const tool = input.tool
    
    if (tool === 'write' || tool === 'edit') {
      const filePath = input.args?.filePath || ''
      const isCoreFile = CORE_PATTERNS.some(p => filePath.includes(p))
      
      if (isCoreFile) {
        await client.tui.showToast({
          body: {
            title: '备份提醒',
            message: `即将修改核心文件: ${filePath}\n建议: git tag "backup/$(date +%Y%m%d-%H%M%S)"\n可用 /undo 撤销`,
            variant: 'warning',
          }
        })
      }
    }
  },

  'tool.execute.after': async (input) => {
    const tool = input.tool
    
    if (tool === 'bash') {
      const command = input.args?.command || ''
      
      if (command.includes('git commit') && !command.includes('--no-verify')) {
        await client.tui.showToast({
          body: {
            title: '提交成功',
            message: 'git push 同步到远程仓库，或 git log 查看历史',
            variant: 'success',
          }
        })
      }
    }
  }
})
