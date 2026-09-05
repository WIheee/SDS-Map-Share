/**
 * 主题相关的共享常量与工具（main.ts / App.vue / SettingsView 共用）
 * 统一管理：预设主题色、localStorage key、安全读写工具
 */

export type Theme = 'light' | 'dark' | 'auto'

export type ColorPreset = 'purple' | 'blue' | 'green' | 'pink'

export const colorPresets: Record<ColorPreset, string> = {
  purple: '#6750A4',
  blue: '#0061A4',
  green: '#1E7A5E',
  pink: '#B93A6C',
}

/** localStorage key 集中管理，避免魔法字符串散落各处 */
export const STORAGE_KEYS = {
  theme: 'theme',
  colorScheme: 'colorScheme',
} as const

/** 安全读取 localStorage（隐私模式 / 存储被禁用时返回 null，不抛异常） */
export function safeGetItem(key: string): string | null {
  try {
    return localStorage.getItem(key)
  } catch {
    return null
  }
}

/** 安全写入 localStorage（存储不可用时静默降级，不抛异常） */
export function safeSetItem(key: string, value: string): void {
  try {
    localStorage.setItem(key, value)
  } catch {
    // 配额满 / 隐私模式 / 存储被禁用时静默失败
  }
}
