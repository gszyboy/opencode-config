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

export default async (ctx) => ({
  'tool.execute.after': async (input, output) => {
    const tool = input.tool
    const args = input.args || {}
    
    // 记录写操作
    if (tool === 'write' || tool === 'edit') {
      const filePath = args.filePath || ''
      const isImportant = TRACKED_PATTERNS.some(p => filePath.toLowerCase().includes(p))
      
      if (isImportant) {
        console.log(`\n📝 [安全日志] 修改重要文件: ${filePath}`)
        console.log(`   时间: ${new Date().toISOString()}`)
        console.log(`   工具: ${tool}`)
      }
    }
    
    // 记录删除操作
    if (tool === 'bash') {
      const command = args.command || ''
      const isDangerous = DANGEROUS_COMMANDS.some(cmd => command.includes(cmd))
      
      if (isDangerous || command.includes('rm ')) {
        console.log(`\n⚠️  [警告] 执行潜在危险命令:`)
        console.log(`   命令: ${command}`)
        console.log(`   时间: ${new Date().toISOString()}`)
        console.log(`   建议: 确保已备份，或使用 /undo 可撤销`)
      }
    }
  },

  'session.created': async (event) => {
    console.log(`\n🔒 安全插件已加载 - 文件操作将被监控`)
  }
})
