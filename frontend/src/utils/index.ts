/**
 * 格式化文件大小
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

/**
 * 格式化时间
 */
export function formatTime(ms: number): string {
  if (ms < 1) return `${(ms * 1000).toFixed(2)} μs`
  if (ms < 1000) return `${ms.toFixed(4)} ms`
  if (ms < 60000) return `${(ms / 1000).toFixed(2)} s`
  
  const minutes = Math.floor(ms / 60000)
  const seconds = ((ms % 60000) / 1000).toFixed(0)
  return `${minutes}:${seconds.padStart(2, '0')}`
}

/**
 * 格式化百分比
 */
export function formatPercent(value: number, decimals: number = 2): string {
  return `${value.toFixed(decimals)}%`
}

/**
 * 深拷贝对象
 */
export function deepClone<T>(obj: T): T {
  if (obj === null || typeof obj !== 'object') return obj
  if (obj instanceof Date) return new Date(obj.getTime()) as unknown as T
  if (obj instanceof Array) return obj.map(item => deepClone(item)) as unknown as T
  if (typeof obj === 'object') {
    const copy = {} as { [key: string]: any }
    Object.keys(obj).forEach(key => {
      copy[key] = deepClone((obj as { [key: string]: any })[key])
    })
    return copy as T
  }
  return obj
}

/**
 * 防抖函数
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null
  
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

/**
 * 节流函数
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean
  
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

/**
 * 生成唯一ID
 */
export function generateId(): string {
  return Math.random().toString(36).substr(2, 9)
}

/**
 * 验证JSON字符串
 */
export function isValidJSON(str: string): boolean {
  try {
    JSON.parse(str)
    return true
  } catch {
    return false
  }
}

/**
 * 下载文件
 */
export function downloadFile(url: string, filename: string): void {
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.target = '_blank'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

/**
 * 复制到剪贴板
 */
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch {
    // 降级方案
    const textArea = document.createElement('textarea')
    textArea.value = text
    document.body.appendChild(textArea)
    textArea.select()
    const success = document.execCommand('copy')
    document.body.removeChild(textArea)
    return success
  }
}

/**
 * 算法状态相关工具
 */
export const AlgorithmUtils = {
  getStatusType(status: string): string {
    const typeMap: Record<string, string> = {
      'PENDING': 'info',
      'RUNNING': 'warning',
      'COMPLETED': 'success',
      'FAILED': 'danger'
    }
    return typeMap[status] || 'info'
  },

  getStatusText(status: string): string {
    const textMap: Record<string, string> = {
      'PENDING': '待运行',
      'RUNNING': '运行中',
      'COMPLETED': '已完成',
      'FAILED': '失败'
    }
    return textMap[status] || status
  },

  getCategoryText(category: string): string {
    const categoryMap: Record<string, string> = {
      'KEM': 'KEM (密钥封装)',
      'SIGNATURE': '数字签名'
    }
    return categoryMap[category] || category
  }
}