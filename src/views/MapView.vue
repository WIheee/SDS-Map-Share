<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { CATEGORIES } from '@/constants/map'
import { useMapsStore } from '@/stores/maps'
import { useFavoritesStore } from '@/stores/favorites'
import 'mdui/components/text-field.js'
import 'mdui/components/select.js'
import 'mdui/components/menu-item.js'
import 'mdui/components/card.js'
import 'mdui/components/icon.js'
import 'mdui/components/divider.js'
import 'mdui/components/circular-progress.js'

defineOptions({ name: 'MapView' })

const router = useRouter()
const mapsStore = useMapsStore()
const favoritesStore = useFavoritesStore()

const FAV = '__favorite__'
const selectedCategory = ref<string>('')
const searchQuery = ref('')

mapsStore.loadMaps()

const maps = computed(() => mapsStore.maps)
const loading = computed(() => !mapsStore.loaded)

// 下拉选项：占位 + 全部 + 收藏（带图标）+ 各分类
const categoryOptions = [
  { value: '', label: '选择你想要的分类', disabled: true },
  { value: '', label: '全部' },
  { value: FAV, label: '收藏', icon: 'favorite' },
  ...CATEGORIES.map((cat) => ({ value: cat, label: cat })),
]

const filteredMaps = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  return maps.value.filter((map) => {
    if (selectedCategory.value === FAV && !favoritesStore.has(map.id)) return false
    if (selectedCategory.value !== FAV && selectedCategory.value) {
      if (!map.category.includes(selectedCategory.value)) return false
    }
    if (!query) return true
    return (
      map.title.toLowerCase().includes(query) ||
      map.description.toLowerCase().includes(query) ||
      map.author.toLowerCase().includes(query)
    )
  })
})

const onCategoryChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  selectedCategory.value = target.value
}

const goToDetail = (id: number) => {
  router.push(`/map/${id}`)
}

const toggleFavorite = (id: number, event: Event) => {
  event.stopPropagation()
  event.preventDefault()
  favoritesStore.toggle(id)
  ;(event.currentTarget as HTMLElement | null)?.blur?.()
}
</script>

<template>
  <div class="map-view">
    <div class="header">
      <mdui-icon name="map" class="header-icon" aria-hidden="true"></mdui-icon>
      <h1>地图资源</h1>
    </div>

    <div class="filter-row">
      <mdui-text-field
        v-model="searchQuery"
        placeholder="搜索地图、作者..."
        clearable
        icon="search"
        aria-label="搜索地图"
        class="search-box"
      ></mdui-text-field>

      <mdui-select
        :value="selectedCategory"
        @change="onCategoryChange"
        class="category-select"
        aria-label="选择分类"
      >
        <mdui-menu-item
          v-for="opt in categoryOptions"
          :key="opt.label"
          :value="opt.value"
          :disabled="opt.disabled"
        >
          <mdui-icon v-if="opt.icon" :name="opt.icon" slot="icon"></mdui-icon>
          {{ opt.label }}
        </mdui-menu-item>
      </mdui-select>
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
        <img :src="map.image" :alt="map.title" class="card-image" loading="lazy" />
        <button
          type="button"
          class="fav-btn"
          :class="{ active: favoritesStore.has(map.id) }"
          :aria-label="favoritesStore.has(map.id) ? '取消收藏' : '收藏'"
          :aria-pressed="favoritesStore.has(map.id)"
          @click.stop.prevent="toggleFavorite(map.id, $event)"
          @keydown.stop
          @keydown.enter.stop.prevent="toggleFavorite(map.id, $event)"
          @keydown.space.stop.prevent="toggleFavorite(map.id, $event)"
        >
          <mdui-icon
            :name="favoritesStore.has(map.id) ? 'favorite' : 'favorite_border'"
          ></mdui-icon>
        </button>
        <div class="card-content">
          <div class="card-header">
            <h3>{{ map.title }}</h3>
            <mdui-icon name="chevron_right" class="arrow-icon"></mdui-icon>
          </div>
          <mdui-divider></mdui-divider>
          <p>{{ map.description.slice(0, 20) }}{{ map.description.length > 20 ? '...' : '' }}</p>
          <div class="card-footer">
            <span class="category-tag">{{ map.category.join(' · ') }}</span>
            <span class="author-tag">{{ map.author }}</span>
          </div>
        </div>
      </mdui-card>

      <div v-if="filteredMaps.length === 0" class="empty-state">
        <p>{{ selectedCategory === FAV ? '还没有收藏任何地图' : '没有找到匹配的地图' }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.map-view {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  box-sizing: border-box;
  color: rgb(var(--mdui-color-on-surface));
  background: rgb(var(--mdui-color-surface));
}

.header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
  width: 100%;
  justify-content: center;
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

.filter-row {
  display: flex;
  gap: 12px;
  width: 100%;
  max-width: 600px;
  margin-bottom: 20px;
}

.search-box {
  flex: 1;
  min-width: 0;
}

.category-select {
  width: 200px;
  flex-shrink: 0;
}

.card-grid {
  display: grid;
  width: 100%;
  gap: 16px;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
}

.map-card {
  position: relative;
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
  height: 150px;
  object-fit: cover;
  display: block;
}

.fav-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 1;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  padding: 0;
  background: rgba(0, 0, 0, 0.35);
  color: #fff;
  transition:
    transform 0.15s ease,
    background-color 0.2s ease;
}

.fav-btn:hover {
  transform: scale(1.12);
  background: rgba(0, 0, 0, 0.5);
}

.fav-btn.active {
  color: rgb(var(--mdui-color-primary));
}

.fav-btn mdui-icon {
  font-size: 20px;
  pointer-events: none;
}

.card-content {
  padding: 12px 16px 16px;
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
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.category-tag {
  font-size: 12px;
  padding: 2px 12px;
  border-radius: 12px;
  background: rgb(var(--mdui-color-primary-container));
  color: rgb(var(--mdui-color-on-primary-container));
}

.author-tag {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 12px;
  background: rgb(var(--mdui-color-surface-container));
  color: rgb(var(--mdui-color-on-surface-variant));
  opacity: 0.8;
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

  .filter-row {
    flex-direction: column;
    gap: 10px;
  }

  .category-select {
    width: 100%;
  }

  .card-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .card-image {
    height: 120px;
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