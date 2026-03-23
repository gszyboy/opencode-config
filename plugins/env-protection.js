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

export const EnvProtection = async ({ client }) => ({
  'tool.execute.before': async (input) => {
    const tool = input.tool
    
    if (tool === 'read') {
      const filePath = input.args?.filePath || ''
      if (isSensitivePath(filePath)) {
        await client.tui.showToast({
          body: {
            title: '敏感文件访问被阻止',
            message: filePath,
            variant: 'error',
          }
        })
        throw new Error(`⛔ 敏感文件访问被阻止: ${filePath}\n如需访问敏感文件，请确保用户明确授权。\n提示：手动复制文件内容给 AI。`)
      }
    }
    
    if (tool === 'write' || tool === 'edit') {
      const filePath = input.args?.filePath || ''
      if (isSensitivePath(filePath) && !filePath.includes('.env.example')) {
        await client.tui.showToast({
          body: {
            title: '禁止写入敏感文件',
            message: filePath,
            variant: 'error',
          }
        })
        throw new Error(`⛔ 禁止写入敏感文件: ${filePath}\n请使用 .env.example 作为模板文件。`)
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
