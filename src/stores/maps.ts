import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { MapItem } from '@/types/map'
import { FILE_CATEGORY } from '@/constants/map'

export const useMapsStore = defineStore('maps', () => {
  const maps = ref<MapItem[]>([])
  const loaded = ref(false)
  const error = ref(false)

  // id -> MapItem 索引（普通闭包变量即可，无需响应式），getMapById 由 O(n) 降为 O(1)
  let index = new Map<string, MapItem>()

  // Promise 单例缓存：防止并发调用（如 MapView 与 MapDetail 同时挂载）重复加载
  let loadPromise: Promise<void> | null = null

  async function loadMaps(): Promise<void> {
    if (loaded.value) return
    if (loadPromise) return loadPromise

    loadPromise = (async () => {
      try {
        const modules = import.meta.glob('@/data/map/json/*.json', { eager: true })
        const all: MapItem[] = []
        const idx = new Map<string, MapItem>()

        for (const path in modules) {
          const filename =
            path
              .split('/')
              .pop()
              ?.replace(/\.json$/, '') ?? ''
          const fileCategory: string | undefined = FILE_CATEGORY[filename]
          const data = (modules[path] as { default?: unknown }).default

          if (!Array.isArray(data)) continue

          for (const raw of data) {
            if (!raw || typeof raw !== 'object') continue
            const item = raw as Record<string, unknown>

            const id = item.id
            const title = item.title
            const image = item.image
            const file = item.file
            if (typeof id !== 'string' || typeof title !== 'string') continue
            if (typeof image !== 'string' || typeof file !== 'string') continue

            let category: string[] = []
            if (typeof item.category === 'string') {
              category = [item.category]
            } else if (Array.isArray(item.category)) {
              category = item.category.filter((c): c is string => typeof c === 'string')
            }
            if (fileCategory && !category.includes(fileCategory)) {
              category.unshift(fileCategory)
            }

            const normalized: MapItem = {
              id,
              title,
              description: typeof item.description === 'string' ? item.description : '',
              image,
              file,
              category,
              author: typeof item.author === 'string' ? item.author : '',
              authorUrl: typeof item.authorUrl === 'string' ? item.authorUrl : '',
            }

            all.push(normalized)
            if (!idx.has(normalized.id)) idx.set(normalized.id, normalized)
          }
        }

        maps.value = all
        index = idx
        loaded.value = true
        error.value = false
      } catch {
        error.value = true
        loaded.value = true
      } finally {
        loadPromise = null
      }
    })()

    return loadPromise
  }

  function getMapById(id: string): MapItem | undefined {
    return index.get(id)
  }

  return { maps, loaded, error, loadMaps, getMapById }
})
