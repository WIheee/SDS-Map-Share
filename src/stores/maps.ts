import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { MapItem } from '@/types/map'
import { FILE_CATEGORY } from '@/constants/map'

/**
 * 地图数据 store（唯一数据源）
 * MapView / MapDetail 统一从这里取数，不再各自重复 import.meta.glob
 */
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
        // 按文件名自动注入分类（battle -> 对战 ...），JSON 中无需再手写 category
        const filename = path.split('/').pop()?.replace(/\.json$/, '') ?? ''
        const data = (modules[path] as { default: MapItem[] }).default
        if (Array.isArray(data)) {
          for (const item of data) {
            all.push({ ...item, category: FILE_CATEGORY[filename] ?? item.category })
          }
        }
      }
      maps.value = all
      loaded.value = true
      error.value = false
    } catch {
      error.value = true
      loaded.value = true // 标记为已尝试加载
    }
  }

  function getMapById(id: number): MapItem | undefined {
    return maps.value.find((m) => m.id === id)
  }

  return { maps, loaded, error, loadMaps, getMapById }
})
