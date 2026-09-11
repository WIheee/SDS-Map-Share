import { defineStore } from 'pinia'
import { ref } from 'vue'
import { safeGetItem, safeSetItem } from '@/constants/theme'

const STORAGE_KEY = 'favoriteMaps'

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
