<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import 'mdui/components/card.js'
import 'mdui/components/button.js'
import 'mdui/components/icon.js'
import 'mdui/components/divider.js'
import 'mdui/components/circular-progress.js'

interface MapItem {
  id: number
  title: string
  description: string
  image: string
  file: string
  category: string
  author: string
}

const route = useRoute()
const router = useRouter()
const mapData = ref<MapItem | null>(null)
const loading = ref(true)
const error = ref(false)

const modules = import.meta.glob('@/data/map/json/*.json', { eager: true })

const loadMap = (id: number) => {
  const allData: MapItem[] = []
  for (const path in modules) {
    const data = (modules[path] as { default: MapItem[] }).default
    if (Array.isArray(data)) {
      allData.push(...data)
    }
  }
  const found = allData.find(item => item.id === id)
  if (found) {
    mapData.value = found
    loading.value = false
  } else {
    error.value = true
    loading.value = false
  }
}

const downloadMap = () => {
  if (!mapData.value) return
  const filePath = mapData.value.file
  const fullPath = import.meta.env.BASE_URL + filePath.replace(/^\//, '')
  fetch(fullPath)
    .then(res => res.blob())
    .then(blob => {
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filePath.split('/').pop() || 'map.map'
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    })
    .catch(() => alert('下载失败，请稍后重试'))
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  const id = parseInt(route.params.id as string)
  if (isNaN(id)) {
    error.value = true
    loading.value = false
    return
  }
  loadMap(id)
  nextTick(() => {
    window.scrollTo(0, 0)
  })
})
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

      <div class="panorama">
        <img :src="mapData.image" :alt="mapData.title" />
      </div>

      <div class="download-section">
        <mdui-button variant="filled" @click="downloadMap" class="download-btn">
          <mdui-icon name="file_download" slot="icon"></mdui-icon>
          下载地图
        </mdui-button>
      </div>

      <mdui-card class="info-card">
        <div class="card-header">
          <mdui-icon name="description" class="card-icon"></mdui-icon>
          <span>描述</span>
        </div>
        <mdui-divider></mdui-divider>
        <div class="card-body">
          {{ mapData.description }}
        </div>
      </mdui-card>

      <mdui-card class="info-card">
        <div class="card-header">
          <mdui-icon name="person" class="card-icon"></mdui-icon>
          <span>作者</span>
        </div>
        <mdui-divider></mdui-divider>
        <div class="card-body">
          {{ mapData.author }}
        </div>
      </mdui-card>
    </div>
  </div>
</template>

<style scoped>
.detail-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px 16px 40px;
  background: rgb(var(--mdui-color-surface));
  color: rgb(var(--mdui-color-on-surface));
  min-height: 100vh;
  box-sizing: border-box;
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
  .detail-page {
    padding: 12px;
  }
  .map-title {
    font-size: 22px;
  }
}
</style>
