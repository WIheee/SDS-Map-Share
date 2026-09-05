import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { MapItem } from '@/types/map'
import { FILE_CATEGORY } from '@/constants/map'

export const useMapsStore = defineStore('maps', () => {
  const maps = ref<MapItem[]>([])
  const loaded = ref(false)
  const error = ref(false)

  // id -> MapItem 索引（普通闭包变量即可，无需响应式），getMapById 由 O(n) 降为 O(1)
  let index = new Map<number, MapItem>()

  async function loadMaps() {
    if (loaded.value) return
    try {
      const modules = import.meta.glob('@/data/map/json/*.json', { eager: true })
      const all: MapItem[] = []
      const idx = new Map<number, MapItem>()

      for (const path in modules) {
        const filename =
          path
            .split('/')
            .pop()
            ?.replace(/\.json$/, '') ?? ''
        // 按 JSON 文件名自动注入分类（FILE_CATEGORY），并与 JSON 内手写的 category 取并集，
        // 避免手写遗漏/写错导致前端筛选失效（对现有正确数据结果完全一致）
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
          // 字段防御：缺关键字段的条目直接跳过，避免下游崩溃
          if (typeof id !== 'number' || typeof title !== 'string') continue
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
          }

          all.push(normalized)
          // 与原 Array.find 语义一致：重复 id 保留最先出现的
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
    }
  }

  function getMapById(id: number): MapItem | undefined {
    return index.get(id)
  }

  return { maps, loaded, error, loadMaps, getMapById }
})
