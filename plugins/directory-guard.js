/**
 * Directory Guard Plugin
 * 
 * 检测危险目录，防止在敏感目录执行操作
 */

const DANGEROUS_PATTERNS = [
  { pattern: /^~$/, reason: '用户根目录，可能污染home文件夹' },
  { pattern: /^~\/$/, reason: '用户根目录，可能污染home文件夹' },
  { pattern: /^\/$/, reason: '系统根目录，危险操作可能破坏系统' },
  { pattern: /^\/home$/, reason: 'home目录太宽泛' },
  { pattern: /^\/home\/[^\/]+$/, reason: '个人目录，不是项目目录' },
  { pattern: /^\/tmp$/, reason: '临时目录，不适合存放代码' },
  { pattern: /^\/etc$/, reason: '系统配置目录，危险' },
  { pattern: /^\/var$/, reason: '系统变量目录，危险' },
  { pattern: /^\/usr$/, reason: '系统程序目录，危险' },
  { pattern: /^\/boot$/, reason: '启动目录，危险' },
  { pattern: /^\/sys$/, reason: '系统内核目录，危险' },
  { pattern: /^\/proc$/, reason: '进程信息目录，危险' },
  { pattern: /^\/dev$/, reason: '设备目录，危险' },
]

let lastWarning = 0

function isDangerousDirectory(dir) {
  for (const { pattern, reason } of DANGEROUS_PATTERNS) {
    if (pattern.test(dir)) {
      return reason
    }
  }
  return null
}

function checkAndWarn(client) {
  const currentDir = process.cwd()
  const danger = isDangerousDirectory(currentDir)
  
  if (danger) {
    const now = Date.now()
    if (now - lastWarning > 60000) {
      lastWarning = now
      client.tui.showToast({
        body: {
          title: '⚠️ 危险目录警告',
          message: `当前目录: ${currentDir}\n原因: ${danger}\n建议: cd 到项目目录再执行 opencode`,
          variant: 'warning',
        }
      })
    }
  }
}

export const DirectoryGuard = async ({ client }) => ({
  event: async ({ event }) => {
    if (event.type === 'session.created') {
      checkAndWarn(client)
    }
  },
  
  'tool.execute.before': async (input) => {
    if (input.tool === 'write' || input.tool === 'edit' || input.tool === 'bash') {
      checkAndWarn(client)
    }
  },
})