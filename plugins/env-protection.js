/**
 * Env Protection Plugin
 * 
 * 保护 .env 文件不被意外读取或修改
 */

const SENSITIVE_PATTERNS = [
  '.env',
  '.env.local',
  '.env.development',
  '.env.production',
  '.env.*',
  'secrets.json',
  'credentials.json',
  '*.key',
  '*.pem',
  'id_rsa*',
  '*.secret',
  'passwords.json'
]

function isSensitivePath(filePath) {
  return SENSITIVE_PATTERNS.some(pattern => {
    if (pattern.includes('*')) {
      const regex = new RegExp('^' + pattern.replace(/\*/g, '.*') + '$')
      return regex.test(filePath)
    }
    return filePath.includes(pattern)
  })
}

export default async (ctx) => ({
  'tool.execute.before': async (input) => {
    const tool = input.tool
    
    // 检查读操作
    if (tool === 'read') {
      const filePath = input.args?.filePath || ''
      if (isSensitivePath(filePath)) {
        throw new Error(
          `⛔ 敏感文件访问被阻止: ${filePath}\n` +
          `如需访问敏感文件，请确保用户明确授权。\n` +
          `提示：手动复制文件内容给 AI。`
        )
      }
    }
    
    // 检查写操作
    if (tool === 'write' || tool === 'edit') {
      const filePath = input.args?.filePath || ''
      if (isSensitivePath(filePath) && !filePath.includes('.env.example')) {
        throw new Error(
          `⛔ 禁止写入敏感文件: ${filePath}\n` +
          `请使用 .env.example 作为模板文件。`
        )
      }
    }
  },

  'permission.asked': async (event) => {
    if (event.permission === 'read' && isSensitivePath(event.resource)) {
      return {
        granted: false,
        reason: '敏感文件需要明确授权'
      }
    }
  }
})
