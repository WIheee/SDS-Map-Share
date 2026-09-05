import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { MapItem } from '@/types/map'
import { FILE_CATEGORY } from '@/constants/map'

export const useMapsStore = defineStore('maps', () => {
  const maps = ref<MapItem[]>([])
  const loaded = ref(false)
  const error = ref(false)

  async function loadMaps() {
    if (loaded.value) return
    try {
      const modules = import.meta.glob('@/data/map/json/*.json', { eager: true })
      const all: MapItem[] = []
      for (const path in modules) {
        const filename =
          path
            .split('/')
            .pop()
            ?.replace(/\.json$/, '') ?? ''
        const data = (modules[path] as { default: MapItem[] }).default
        if (Array.isArray(data)) {
          for (const item of data) {
            // 确保 category 是数组
            let cat = item.category
            if (typeof cat === 'string') cat = [cat]
            else if (!Array.isArray(cat)) cat = []
            all.push({ ...item, category: cat })
          }
        }
      }
      maps.value = all
      loaded.value = true
      error.value = false
    } catch {
      error.value = true
      loaded.value = true
    }
  }

  function getMapById(id: number): MapItem | undefined {
    return maps.value.find((m) => m.id === id)
  }

  return { maps, loaded, error, loadMaps, getMapById }
})
