<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Giscus from '@giscus/vue'
import type { MapItem } from '@/types/map'
import { useMapsStore } from '@/stores/maps'
import { useFavoritesStore } from '@/stores/favorites'
import 'mdui/components/card.js'
import 'mdui/components/button.js'
import 'mdui/components/icon.js'
import 'mdui/components/divider.js'
import 'mdui/components/circular-progress.js'
import 'mdui/components/snackbar.js'

const route = useRoute()
const router = useRouter()
const mapsStore = useMapsStore()
const favoritesStore = useFavoritesStore()

const mapData = ref<MapItem | null>(null)
const loading = ref(true)
const error = ref(false)
const downloading = ref(false)
const showHint = ref(false)

const isFavorite = computed(() => (mapData.value ? favoritesStore.has(mapData.value.id) : false))

const toggleFavorite = () => {
  if (mapData.value) favoritesStore.toggle(mapData.value.id)
}

const safeImage = computed(() => mapData.value?.image || '')

const downloadUrl = (file: string): string => {
  const base = import.meta.env.BASE_URL.replace(/\/+$/, '')
  return `${base}${file}`
}

const downloadMap = () => {
  if (!mapData.value || downloading.value) return
  const file = mapData.value.file

  downloading.value = true

  const hadFocus = document.hasFocus()

  const a = document.createElement('a')
  a.href = downloadUrl(file)
  a.download = file.split('/').pop() || 'map.7z'
  a.rel = 'noopener'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)

  setTimeout(() => {
    downloading.value = false
  }, 300)

  setTimeout(() => {
    if (hadFocus && document.hasFocus() && !document.hidden) {
      showHint.value = true
    }
  }, 3000)
}

const goBack = () => {
  if (window.history.state?.back) {
    router.back()
  } else {
    router.replace('/map')
  }
}

const loadMap = async () => {
  loading.value = true
  await mapsStore.loadMaps()
  const raw = route.params.id
  const idStr = Array.isArray(raw) ? raw[0] : raw
  const id = parseInt(idStr ?? '', 10)
  const found = Number.isNaN(id) ? undefined : mapsStore.getMapById(id)
  mapData.value = found ?? null
  error.value = !found
  loading.value = false
}

onMounted(loadMap)

watch(
  () => route.params.id,
  () => {
    if (route.name === 'mapDetail') void loadMap()
  },
)
</script>

<template>
  <div class="detail-page">
    <div class="back-bar">
      <mdui-button
        variant="text"
        icon="arrow_back"
        @click="goBack"
        class="back-btn"
        aria-label="返回地图列表"
      ></mdui-button>
    </div>

    <div v-if="loading" class="loading-state">
      <mdui-circular-progress></mdui-circular-progress>
    </div>

    <div v-else-if="error" class="error-state">
      <p>地图不存在或加载失败</p>
      <mdui-button variant="text" @click="goBack">返回</mdui-button>
    </div>

    <div v-else-if="mapData" class="detail-content">
      <h1 class="map-title">{{ mapData.title }}</h1>

      <div class="category-badges">
        <span v-for="cat in mapData.category" :key="cat" class="detail-category-tag">
          {{ cat }}
        </span>
      </div>

      <div class="panorama">
        <img v-if="safeImage" :src="safeImage" :alt="mapData.title" />
      </div>

      <div class="download-section">
        <mdui-button
          variant="filled"
          :disabled="downloading"
          @click="downloadMap"
          class="download-btn"
        >
          <mdui-icon
            :name="downloading ? 'hourglass_empty' : 'file_download'"
            slot="icon"
          ></mdui-icon>
          {{ downloading ? '下载中...' : '下载地图' }}
        </mdui-button>
        <mdui-button
          :variant="isFavorite ? 'filled-tonal' : 'outlined'"
          @click="toggleFavorite"
          class="fav-btn"
          :aria-pressed="isFavorite"
          :aria-label="isFavorite ? '取消收藏' : '收藏'"
        >
          <mdui-icon :name="isFavorite ? 'favorite' : 'favorite_border'" slot="icon"></mdui-icon>
          {{ isFavorite ? '已收藏' : '收藏' }}
        </mdui-button>
      </div>

      <mdui-card class="info-card">
        <div class="card-header">
          <mdui-icon name="description" class="card-icon"></mdui-icon>
          <span>描述</span>
        </div>
        <mdui-divider></mdui-divider>
        <div class="card-body">{{ mapData.description }}</div>
      </mdui-card>

      <mdui-card class="info-card">
        <div class="card-header">
          <mdui-icon name="person" class="card-icon"></mdui-icon>
          <span>作者</span>
        </div>
        <mdui-divider></mdui-divider>
        <div class="card-body">{{ mapData.author }}</div>
      </mdui-card>

      <!-- ====== 评论区域 ====== -->
      <div class="giscus-container" style="margin-top: 24px; width: 100%">
        <Giscus
          :key="mapData.id"
          id="comments"
          repo="WIheee/SDS-Map-Share"
          repoId="R_kgDOUPE0UA"
          category="Q&A"
          categoryId="DIC_kwDOUPE0UM4DE8Ib"
          mapping="specific"
          :term="String(mapData.id)"
          reactionsEnabled="1"
          emitMetadata="0"
          inputPosition="bottom"
          theme="fro"
          lang="zh-CN"
          loading="lazy"
        />
      </div>
    </div>

    <mdui-snackbar v-model="showHint" placement="top" :timeout="4000" closeable
      >若浏览器未开始下载，请检查网络后重试</mdui-snackbar
    >
  </div>
</template>

<style scoped>
.detail-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px 16px 40px;
  box-sizing: border-box;
  min-height: calc(100vh - 160px);
  background: rgb(var(--mdui-color-surface));
  color: rgb(var(--mdui-color-on-surface));
}

.back-bar {
  display: flex;
  align-items: center;
  width: 100%;
  margin-bottom: 20px;
}

.back-btn {
  min-width: 56px !important;
  height: 56px !important;
  border-radius: 50% !important;
  padding: 0 !important;
  --mdui-button-icon-size: 28px;
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  color: rgb(var(--mdui-color-on-surface-variant));
}

.detail-content {
  width: 100%;
}

.map-title {
  font-size: 28px;
  text-align: center;
  margin: 0 0 8px 0;
  color: rgb(var(--mdui-color-on-surface));
}

.category-badges {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 6px;
  margin-bottom: 16px;
}

.detail-category-tag {
  font-size: 13px;
  padding: 2px 14px;
  border-radius: 14px;
  background: rgb(var(--mdui-color-primary-container));
  color: rgb(var(--mdui-color-on-primary-container));
}

.panorama {
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 20px;
  background: rgb(var(--mdui-color-surface-container));
}

.panorama img {
  width: 100%;
  height: auto;
  display: block;
}

.download-section {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 24px;
}

.download-btn {
  min-width: 160px;
}

.info-card {
  padding: 16px;
  margin-bottom: 16px;
  background: rgb(var(--mdui-color-surface-container));
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  color: rgb(var(--mdui-color-on-surface-variant));
  font-size: 14px;
}

.card-icon {
  font-size: 20px;
  color: rgb(var(--mdui-color-primary));
}

.card-body {
  padding-top: 12px;
  font-size: 16px;
  line-height: 1.6;
  color: rgb(var(--mdui-color-on-surface));
}

@media (max-width: 600px) {
  .map-title {
    font-size: 22px;
  }
}
</style>
