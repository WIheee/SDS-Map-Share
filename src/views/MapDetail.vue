<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { MapItem } from '@/types/map'
import { useMapsStore } from '@/stores/maps'
import 'mdui/components/card.js'
import 'mdui/components/button.js'
import 'mdui/components/icon.js'
import 'mdui/components/divider.js'
import 'mdui/components/circular-progress.js'

const route = useRoute()
const router = useRouter()
const mapsStore = useMapsStore()

const mapData = ref<MapItem | null>(null)
const loading = ref(true)
const error = ref(false)
const downloading = ref(false)

// ===== Giscus 评论（按地图 ID 隔离）=====
const loadGiscus = () => {
  if (!mapData.value) return
  
  const container = document.querySelector('.giscus-container')
  if (!container) return
  container.innerHTML = ''
  
  const oldScript = document.querySelector('#giscus-script')
  if (oldScript) oldScript.remove()
  
  const script = document.createElement('script')
  script.id = 'giscus-script'
  script.src = 'https://giscus.app/client.js'
  script.setAttribute('data-repo', 'WIheee/SDS-Map-Share')
  script.setAttribute('data-repo-id', 'R_kgDOUPE0UA')
  script.setAttribute('data-category', 'Announcements')
  script.setAttribute('data-category-id', 'DIC_kwDOUPE0UM4DE8IZ')
  script.setAttribute('data-mapping', 'specific')
  // ★ 关键：使用地图 ID 作为唯一标识
  script.setAttribute('data-term', String(mapData.value.id))
  script.setAttribute('data-strict', '0')
  script.setAttribute('data-reactions-enabled', '1')
  script.setAttribute('data-emit-metadata', '0')
  script.setAttribute('data-input-position', 'bottom')
  script.setAttribute('data-theme', 'preferred_color_scheme')
  script.setAttribute('data-lang', 'zh-CN')
  script.setAttribute('data-loading', 'lazy')
  script.crossOrigin = 'anonymous'
  script.async = true
  
  container.appendChild(script)
}

// 地图切换时重新加载评论
watch(() => mapData.value, (newVal) => {
  if (newVal) {
    nextTick(() => { loadGiscus() })
  }
}, { immediate: true })

// ===== 下载 =====
const downloadMap = () => {
  if (!mapData.value || downloading.value) return
  downloading.value = true
  const a = document.createElement('a')
  a.href = import.meta.env.BASE_URL + mapData.value.file.replace(/^\//, '')
  a.download = mapData.value.file.split('/').pop() ?? 'map.7z'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  setTimeout(() => { downloading.value = false }, 1500)
}

const goBack = () => {
  if (window.history.state?.back) {
    router.back()
  } else {
    router.replace('/map')
  }
}

onMounted(async () => {
  await mapsStore.loadMaps()
  const id = parseInt(route.params.id as string)
  const found = isNaN(id) ? undefined : mapsStore.getMapById(id)
  if (found) {
    mapData.value = found
    error.value = false
  } else {
    error.value = true
  }
  loading.value = false
})
</script>

<template>
  <div class="detail-page">
    <div class="back-bar">
      <mdui-button variant="text" icon="arrow_back" @click="goBack" class="back-btn" aria-label="返回地图列表"></mdui-button>
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

      <div class="panorama">
        <img :src="mapData.image" :alt="mapData.title" />
      </div>

      <div class="download-section">
        <mdui-button variant="filled" :disabled="downloading" @click="downloadMap" class="download-btn">
          <mdui-icon :name="downloading ? 'hourglass_empty' : 'file_download'" slot="icon"></mdui-icon>
          {{ downloading ? '下载中...' : '下载地图' }}
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
      <div class="giscus-container" style="margin-top: 24px; width: 100%;"></div>
    </div>
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
  margin: 0 0 16px 0;
  color: rgb(var(--mdui-color-on-surface));
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
  text-align: center;
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