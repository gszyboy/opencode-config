/**
 * Sensitive Files Logger Plugin
 * 
 * 记录对重要文件的操作，用于安全审计
 */

const TRACKED_PATTERNS = [
  'database',
  'auth',
  'config',
  'secret',
  'password',
  'payment',
  'order',
  'finance',
  'models.',
  'router.',
  'middleware'
]

const DANGEROUS_COMMANDS = [
  'rm -rf',
  'drop table',
  'delete from',
  'truncate',
  'sudo',
  'chmod 777',
  ':(){:|:&};:'
]

export const SensitiveFilesLogger = async ({ client }) => ({
  'tool.execute.after': async (input) => {
    const tool = input.tool
    const args = input.args || {}
    
    if (tool === 'write' || tool === 'edit') {
      const filePath = args.filePath || ''
      const isImportant = TRACKED_PATTERNS.some(p => filePath.toLowerCase().includes(p))
      
      if (isImportant) {
        await client.tui.showToast({
          body: {
            title: '安全日志',
            message: `修改重要文件: ${filePath}`,
            variant: 'info',
          }
        })
      }
    }
    
    if (tool === 'bash') {
      const command = args.command || ''
      const isDangerous = DANGEROUS_COMMANDS.some(cmd => command.includes(cmd))
      
      if (isDangerous || command.includes('rm ')) {
        await client.tui.showToast({
          body: {
            title: '⚠️ 危险命令警告',
            message: command,
            variant: 'error',
          }
        })
      }
    }
  },

  'session.created': async () => {
    await client.tui.showToast({
      body: {
        title: '安全插件已加载',
        message: '文件操作将被监控',
        variant: 'info',
      }
    })
  }
})
