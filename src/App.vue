<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import 'mdui/components/navigation-bar.js'
import 'mdui/components/navigation-bar-item.js'

const route = useRoute()
const router = useRouter()

// 根据当前路径计算激活的 tab 值，默认 'map'
const activeTab = computed(() => {
  const path = route.path.replace('/', '') || 'map'
  // 确保只返回我们定义的四个值之一，防止路由不匹配时高亮错误
  return ['map', 'activity', 'announcement', 'settings'].includes(path) ? path : 'map'
})

const onTabChange = (event: Event) => {
  const detail = (event as CustomEvent).detail
  const target = event.target as HTMLElement & { value?: string }
  const newTab = detail?.value ?? target?.value
  if (newTab) {
    router.push(`/${newTab}`)
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

    <mdui-navigation-bar
      placement="bottom"
      :value="activeTab"
      @change="onTabChange"
    >
      <mdui-navigation-bar-item 
        value="map" 
        icon="map" 
        label="地图资源" 
      />
      <mdui-navigation-bar-item 
        value="activity" 
        icon="event" 
        label="活动" 
      />
      <mdui-navigation-bar-item 
        value="announcement" 
        icon="announcement" 
        label="公告/关于" 
      />
      <mdui-navigation-bar-item 
        value="settings" 
        icon="settings" 
        label="网站设置" 
      />
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
  padding: 20px;
  padding-bottom: 80px; /* 留出底部导航栏的空间 */
  overflow-y: auto;
  color: rgb(var(--mdui-color-on-surface));
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
