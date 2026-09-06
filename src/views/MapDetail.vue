<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Giscus from '@giscus/vue'
import type { MapItem } from '@/types/map'
import { useMapsStore } from '@/stores/maps'
import { useFavoritesStore } from '@/stores/favorites'
import 'mdui/components/button.js'
import 'mdui/components/button-icon.js'
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

/**
 * 点击作者：
 * - 有 authorUrl → 新窗口打开社交媒体链接
 * - 没有 authorUrl → 跳转到地图列表并搜索该作者
 */
const goToAuthor = () => {
  if (!mapData.value) return

  const url = mapData.value.authorUrl
  if (url) {
    window.open(url, '_blank', 'noopener,noreferrer')
  } else {
    router.push({
      path: '/map',
      query: { author: mapData.value.author },
    })
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
    <!-- 顶部：返回按钮 + 16:9 图片 -->
    <div class="top-section">
      <mdui-button-icon
        class="back-btn"
        variant="standard"
        icon="arrow_back"
        @click="goBack"
        aria-label="返回"
      ></mdui-button-icon>
      <div class="image-wrapper">
        <img
          v-if="safeImage"
          :src="safeImage"
          :alt="mapData?.title || '地图图片'"
          class="map-image"
          loading="lazy"
        />
        <div v-else class="image-placeholder">
          <mdui-icon name="image" class="placeholder-icon"></mdui-icon>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <mdui-circular-progress></mdui-circular-progress>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-state">
      <p>地图不存在或加载失败</p>
      <mdui-button variant="text" @click="goBack">返回</mdui-button>
    </div>

    <!-- 内容 -->
    <template v-else-if="mapData">
      <!-- 按钮组：下载 + 收藏 -->
      <div class="button-group">
        <mdui-button
          variant="filled"
          :disabled="downloading"
          @click="downloadMap"
          class="btn-download"
        >
          <mdui-icon
            :name="downloading ? 'hourglass_empty' : 'file_download'"
            slot="icon"
          ></mdui-icon>
          {{ downloading ? '下载中...' : '下载' }}
        </mdui-button>
        <mdui-button
          :variant="isFavorite ? 'filled' : 'outlined'"
          @click="toggleFavorite"
          class="btn-favorite"
          :aria-pressed="isFavorite"
        >
          <mdui-icon :name="isFavorite ? 'favorite' : 'favorite_border'" slot="icon"></mdui-icon>
          {{ isFavorite ? '已收藏' : '收藏' }}
        </mdui-button>
      </div>

      <!-- 容器框：标题 + 分割线 + 描述 -->
      <div class="info-container">
        <div class="container-title">{{ mapData.title }}</div>
        <mdui-divider class="container-divider"></mdui-divider>
        <div class="container-description">{{ mapData.description }}</div>
      </div>

      <!-- 作者列表项 - 点击跳转 -->
      <div
        class="author-item"
        @click="goToAuthor"
        role="button"
        tabindex="0"
        :aria-label="
          mapData.authorUrl ? `访问 ${mapData.author} 的主页` : `查看 ${mapData.author} 的所有地图`
        "
      >
        <div class="author-avatar">
          <mdui-icon name="person" class="author-icon"></mdui-icon>
        </div>
        <div class="author-info">
          <div class="author-label">作者</div>
          <div class="author-name">
            {{ mapData.author }}
            <mdui-icon
              v-if="mapData.authorUrl"
              name="open_in_new"
              class="external-icon"
            ></mdui-icon>
          </div>
        </div>
        <mdui-icon name="chevron_right" class="author-arrow"></mdui-icon>
      </div>

      <!-- 评论区域 -->
      <div class="giscus-container">
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
    </template>

    <!-- 下载提示 -->
    <mdui-snackbar v-model="showHint" placement="top" :timeout="4000" closeable>
      若浏览器未开始下载，请检查网络后重试
    </mdui-snackbar>
  </div>
</template>

<style scoped>
.detail-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 412px;
  margin: 0 auto;
  padding: 16px;
  padding-bottom: 40px;
  box-sizing: border-box;
  min-height: calc(100vh - 160px);
  background: rgb(var(--mdui-color-surface));
  color: rgb(var(--mdui-color-on-surface));
}

.top-section {
  position: relative;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
}

.back-btn {
  position: absolute;
  top: 8px;
  left: 8px;
  width: 48px !important;
  height: 48px !important;
  border-radius: 50% !important;
  --mdui-button-icon-size: 24px;
  z-index: 2;
  background: rgba(var(--mdui-color-surface-container), 0.8);
  backdrop-filter: blur(4px);
}

.back-btn::part(button) {
  border-radius: 50% !important;
}

.back-btn:active {
  transform: scale(0.92);
  transition: transform 0.15s ease;
}

.image-wrapper {
  width: 100%;
  aspect-ratio: 16 / 9;
  border-radius: 20px;
  overflow: hidden;
  background: rgb(var(--mdui-color-surface-container-high));
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.map-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgb(var(--mdui-color-on-surface-variant));
}

.placeholder-icon {
  font-size: 48px;
  opacity: 0.5;
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  width: 100%;
  color: rgb(var(--mdui-color-on-surface-variant));
}

.error-state {
  gap: 16px;
}

.button-group {
  display: flex;
  gap: 3px;
  margin-bottom: 16px;
  width: 100%;
  max-width: 380px;
}

.button-group mdui-button {
  flex: 1;
  height: 56px;
  border-radius: 28px !important;
  font-size: 16px;
  font-weight: 500;
  transition: transform 0.15s ease;
}

.button-group mdui-button:active {
  transform: scale(0.96);
}

.btn-download {
  --mdui-button-container-color: rgb(var(--mdui-color-primary));
  --mdui-button-label-text-color: rgb(var(--mdui-color-on-primary));
  border-radius: 28px 8px 8px 28px !important;
}

.btn-download::part(button) {
  border-radius: 28px 8px 8px 28px !important;
}

.btn-download[disabled] {
  opacity: 0.6;
}

.btn-favorite {
  --mdui-button-outline-color: rgb(var(--mdui-color-outline));
  --mdui-button-label-text-color: rgb(var(--mdui-color-on-surface-variant));
  border-radius: 8px 28px 28px 8px !important;
}

.btn-favorite::part(button) {
  border-radius: 8px 28px 28px 8px !important;
}

.btn-favorite[data-variant='filled'] {
  --mdui-button-container-color: rgb(var(--mdui-color-primary));
  --mdui-button-label-text-color: rgb(var(--mdui-color-on-primary));
  border-radius: 8px 28px 28px 8px !important;
}

.btn-favorite[data-variant='filled']::part(button) {
  border-radius: 8px 28px 28px 8px !important;
}

.info-container {
  width: 100%;
  max-width: 380px;
  background: rgb(var(--mdui-color-surface-container-high));
  border-radius: 28px;
  padding: 20px 24px 24px 24px;
  margin-bottom: 16px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.container-title {
  font-size: 28px;
  font-weight: 700;
  color: rgb(var(--mdui-color-on-surface));
  line-height: 1.3;
  margin-bottom: 12px;
  letter-spacing: -0.01em;
}

.container-divider {
  margin: 0 0 12px 0;
  --mdui-divider-color: rgb(var(--mdui-color-outline-variant));
}

.container-description {
  font-size: 18px;
  font-weight: 400;
  color: rgb(var(--mdui-color-on-surface-variant));
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.author-item {
  display: flex;
  align-items: center;
  width: 100%;
  max-width: 380px;
  height: 72px;
  padding: 0 16px;
  background: rgb(var(--mdui-color-surface-container-low));
  border-radius: 28px;
  margin-bottom: 24px;
  box-sizing: border-box;
  transition:
    background 0.2s ease,
    transform 0.15s ease,
    box-shadow 0.2s ease;
  cursor: pointer;
}

.author-item:hover {
  background: rgb(var(--mdui-color-surface-container));
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.author-item:active {
  transform: scale(0.98);
}

.author-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgb(var(--mdui-color-primary-container));
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-right: 12px;
}

.author-icon {
  font-size: 24px;
  color: rgb(var(--mdui-color-on-primary-container));
}

.author-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.author-label {
  font-size: 14px;
  font-weight: 400;
  color: rgb(var(--mdui-color-on-surface-variant));
  line-height: 1.4;
}

.author-name {
  font-size: 16px;
  font-weight: 500;
  color: rgb(var(--mdui-color-primary));
  line-height: 1.4;
  word-break: break-word;
  display: flex;
  align-items: center;
  gap: 4px;
}

.external-icon {
  font-size: 16px;
  color: rgb(var(--mdui-color-primary));
}

.author-arrow {
  font-size: 24px;
  color: rgb(var(--mdui-color-on-surface-variant));
  flex-shrink: 0;
  margin-left: 8px;
}

.giscus-container {
  width: 100%;
  max-width: 380px;
  margin-top: 4px;
}

@media (prefers-color-scheme: dark) {
  .back-btn {
    background: rgba(var(--mdui-color-surface-container), 0.85);
  }

  .image-wrapper {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  }

  .info-container {
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.2);
  }

  .author-item:hover {
    background: rgb(var(--mdui-color-surface-container-high));
  }
}

@media (max-width: 420px) {
  .detail-page {
    padding: 12px 12px 32px 12px;
  }

  .container-title {
    font-size: 24px;
  }

  .container-description {
    font-size: 16px;
  }

  .info-container {
    padding: 16px 18px 18px 18px;
  }

  .button-group mdui-button {
    height: 48px;
    font-size: 14px;
  }

  .author-item {
    height: 64px;
    padding: 0 12px;
  }

  .back-btn {
    top: 4px;
    left: 4px;
    width: 40px !important;
    height: 40px !important;
    --mdui-button-icon-size: 20px;
  }
}

@media (max-width: 360px) {
  .container-title {
    font-size: 20px;
  }

  .container-description {
    font-size: 14px;
  }

  .info-container {
    padding: 14px 14px 16px 14px;
  }
}
</style>
