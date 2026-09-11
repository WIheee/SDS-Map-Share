<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import 'mdui/components/navigation-bar.js'
import 'mdui/components/navigation-bar-item.js'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()

// 详情页 /map/:id 时稳定映射回 'map'，避免底部导航栏指示条抖动
const activeTab = computed(() => {
  const path = route.path.replace(/^\/+/, '')
  if (path === 'map' || path.startsWith('map/')) return 'map'
  return ['activity', 'announcement', 'settings'].includes(path) ? path : 'map'
})

const onTabChange = (event: Event) => {
  const detail = (event as CustomEvent).detail
  const target = event.target as HTMLElement & { value?: string }
  const newTab = detail?.value ?? target?.value
  if (!newTab || typeof newTab !== 'string') return
  // 点击当前已激活的 tab 时直接忽略，避免重复导航导致指示条动画乱跳
  if (newTab === activeTab.value) return
  router.push(`/${newTab}`)
}

onMounted(() => {
  // 确保 html lang 属性与当前语言一致
  document.querySelector('html')?.setAttribute('lang', i18nLocale())
})

function i18nLocale(): string {
  try {
    return localStorage.getItem('locale') || 'zh-CN'
  } catch {
    return 'zh-CN'
  }
}
</script>

<template>
  <div class="app-container">
    <div class="content">
      <router-view v-slot="{ Component }">
        <transition name="fade-slide" mode="out-in">
          <keep-alive include="MapView">
            <component :is="Component" />
          </keep-alive>
        </transition>
      </router-view>
    </div>

    <mdui-navigation-bar placement="bottom" :value="activeTab" @change="onTabChange">
      <mdui-navigation-bar-item value="map" icon="map" :label="t('nav.map')" />
      <mdui-navigation-bar-item value="activity" icon="event" :label="t('nav.activity')" />
      <mdui-navigation-bar-item value="announcement" icon="announcement" :label="t('nav.announcement')" />
      <mdui-navigation-bar-item value="settings" icon="settings" :label="t('nav.settings')" />
    </mdui-navigation-bar>
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: rgb(var(--mdui-color-surface));
}

.content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  padding-top: 40px;
  padding-bottom: 80px;
  color: rgb(var(--mdui-color-on-surface));
  box-sizing: border-box;
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.25s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(12px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-12px);
}

mdui-navigation-bar {
  background-color: rgb(var(--mdui-color-surface-container)) !important;
  border-top: 1px solid rgb(var(--mdui-color-outline-variant));
  box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.1);
}
</style>
