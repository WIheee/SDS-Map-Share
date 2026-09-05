import { defineStore } from 'pinia'
import { ref } from 'vue'

const STORAGE_KEY = 'favoriteMaps'

/** 安全读取 localStorage（隐私模式 / 存储被禁用时返回 null，不抛异常） */
function safeGetItem(key: string): string | null {
  try {
    return localStorage.getItem(key)
  } catch {
    return null
  }
}

/** 安全写入 localStorage（存储不可用时静默降级，不抛异常） */
function safeSetItem(key: string, value: string): void {
  try {
    localStorage.setItem(key, value)
  } catch {
    // 配额满 / 隐私模式 / 存储被禁用时静默失败
  }
}

function loadIds(): number[] {
  const raw = safeGetItem(STORAGE_KEY)
  if (!raw) return []
  try {
    const parsed: unknown = JSON.parse(raw)
    if (!Array.isArray(parsed)) return []
    return parsed.filter((n): n is number => typeof n === 'number')
  } catch {
    return []
  }
}

/**
 * 收藏 store：收藏列表持久化到 localStorage
 * ids 为响应式数组，跨页面/组件共享同一份状态
 */
export const useFavoritesStore = defineStore('favorites', () => {
  const ids = ref<number[]>(loadIds())

  function has(id: number): boolean {
    return ids.value.includes(id)
  }

  function toggle(id: number): void {
    const i = ids.value.indexOf(id)
    if (i === -1) {
      ids.value.push(id)
    } else {
      ids.value.splice(i, 1)
    }
    safeSetItem(STORAGE_KEY, JSON.stringify(ids.value))
  }

  return { ids, has, toggle }
})
