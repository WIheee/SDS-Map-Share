<script setup lang="ts">
import { ref, computed, onMounted, onActivated, onDeactivated, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import 'mdui/components/text-field.js'
import 'mdui/components/segmented-button-group.js'
import 'mdui/components/segmented-button.js'
import 'mdui/components/card.js'
import 'mdui/components/icon.js'
import 'mdui/components/divider.js'
import 'mdui/components/circular-progress.js'

defineOptions({ name: 'MapView' })

interface MapItem {
  id: number
  title: string
  description: string
  image: string
  file: string
  category: string
  author: string
}

const router = useRouter()
const categories = ['对战', '观赏', '机关', '生存']
const selectedCategory = ref<string>('')
const searchQuery = ref('')
const maps = ref<MapItem[]>([])
const loading = ref(true)
const scrollPosition = ref(0)

const modules = import.meta.glob('@/data/map/json/*.json', { eager: true })

const loadData = () => {
  const allData: MapItem[] = []
  for (const path in modules) {
    const data = (modules[path] as { default: MapItem[] }).default
    if (Array.isArray(data)) {
      allData.push(...data)
    }
  }
  maps.value = allData
  loading.value = false
}

const filteredMaps = computed(() => {
  return maps.value.filter((map) => {
    const matchCategory = selectedCategory.value ? map.category === selectedCategory.value : true
    const matchSearch =
      map.title.includes(searchQuery.value) || map.description.includes(searchQuery.value)
    return matchCategory && matchSearch
  })
})

const onCategoryChange = (event: Event) => {
  const detail = (event as CustomEvent).detail
  const target = event.target as HTMLElement & { value?: string }
  const newValue = detail?.value ?? target?.value
  if (typeof newValue === 'string') {
    selectedCategory.value = newValue
  }
}

const goToDetail = (id: number) => {
  router.push(`/map/${id}`)
}

// 保存滚动位置（离开页面时）
onDeactivated(() => {
  const container = document.querySelector('.content') as HTMLElement | null
  scrollPosition.value = container?.scrollTop || 0
})

// 恢复滚动位置（回到页面时）
onActivated(() => {
  nextTick(() => {
    const container = document.querySelector('.content') as HTMLElement | null
    if (container) {
      container.scrollTop = scrollPosition.value
    }
  })
})

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="map-view">
    <div class="header">
      <mdui-icon name="map" class="header-icon" aria-hidden="true"></mdui-icon>
      <h1>Map View</h1>
    </div>

    <div class="search-box">
      <mdui-text-field
        v-model="searchQuery"
        placeholder="搜索地图..."
        clearable
        icon="search"
        aria-label="搜索地图"
      ></mdui-text-field>
    </div>

    <div class="categories">
      <mdui-segmented-button-group
        selects="single"
        :value="selectedCategory"
        @change="onCategoryChange"
      >
        <mdui-segmented-button value="">全部</mdui-segmented-button>
        <mdui-segmented-button v-for="cat in categories" :key="cat" :value="cat">{{
          cat
        }}</mdui-segmented-button>
      </mdui-segmented-button-group>
    </div>

    <div v-if="loading" class="loading-state">
      <mdui-circular-progress></mdui-circular-progress>
    </div>
    <div v-else class="card-grid">
      <mdui-card
        v-for="map in filteredMaps"
        :key="map.id"
        class="map-card"
        role="button"
        tabindex="0"
        :aria-label="`查看地图 ${map.title}`"
        @click="goToDetail(map.id)"
        @keydown.enter="goToDetail(map.id)"
        @keydown.space.prevent="goToDetail(map.id)"
      >
        <img :src="map.image" :alt="map.title" class="card-image" />
        <div class="card-content">
          <div class="card-header">
            <h3>{{ map.title }}</h3>
            <mdui-icon name="chevron_right" class="arrow-icon"></mdui-icon>
          </div>
          <mdui-divider></mdui-divider>
          <p>{{ map.description }}</p>
          <div class="card-footer">
            <span class="category-tag">{{ map.category }}</span>
          </div>
        </div>
      </mdui-card>
      <div v-if="filteredMaps.length === 0" class="empty-state">
        <p>没有找到匹配的地图</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.map-view {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 20px;
  box-sizing: border-box;
  color: rgb(var(--mdui-color-on-surface));
  background: rgb(var(--mdui-color-surface));
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
  width: 100%;
}

.header-icon {
  font-size: 32px;
  color: rgb(var(--mdui-color-primary));
}

h1 {
  font-size: 24px;
  margin: 0;
  color: rgb(var(--mdui-color-on-surface));
}

.search-box {
  width: 100%;
  max-width: 600px;
  margin-bottom: 16px;
}

.categories {
  width: 100%;
  max-width: 600px;
  margin-bottom: 20px;
}

.card-grid {
  display: grid;
  width: 100%;
  gap: 16px;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
}

.map-card {
  overflow: hidden;
  background: rgb(var(--mdui-color-surface-container));
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
  cursor: pointer;
}

.map-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.card-image {
  width: 100%;
  height: 100px;
  object-fit: cover;
  display: block;
}

.card-content {
  padding: 10px 14px 14px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  color: rgb(var(--mdui-color-on-surface));
}

.arrow-icon {
  font-size: 20px;
  color: rgb(var(--mdui-color-primary));
  opacity: 0.6;
}

.card-content p {
  margin: 8px 0 12px 0;
  color: rgb(var(--mdui-color-on-surface-variant));
  font-size: 14px;
  line-height: 1.5;
}

.card-footer {
  display: flex;
  justify-content: flex-end;
}

.category-tag {
  font-size: 12px;
  padding: 2px 12px;
  border-radius: 12px;
  background: rgb(var(--mdui-color-primary-container));
  color: rgb(var(--mdui-color-on-primary-container));
}

.loading-state,
.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 48px 20px;
  color: rgb(var(--mdui-color-on-surface-variant));
}

.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}

@media (max-width: 600px) {
  .map-view {
    padding: 12px;
  }
  .header-icon {
    font-size: 26px;
  }
  h1 {
    font-size: 20px;
  }
  .card-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  .card-image {
    height: 80px;
  }
}

@media (min-width: 601px) and (max-width: 900px) {
  .card-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 901px) {
  .card-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 1200px) {
  .card-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
</style>
