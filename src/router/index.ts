import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/map',
    },
    {
      path: '/map',
      name: 'map',
      component: () => import('../views/MapView.vue'),
    },
    {
      path: '/map/:id',
      name: 'mapDetail',
      component: () => import('../views/MapDetail.vue'),
    },
    {
      path: '/activity',
      name: 'activity',
      component: () => import('../views/ActivityView.vue'),
    },
    {
      path: '/announcement',
      name: 'announcement',
      component: () => import('../views/AnnouncementView.vue'),
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('../views/SettingsView.vue'),
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/map',
    },
  ],
  // 滚动策略：
  // - 浏览器前进/后退：恢复历史位置
  // - 从详情页返回列表：保留滚动位置（取代原先 MapView 中失效的 scrollTop 逻辑）
  // - 其余导航：滚动到顶部（取代原先 MapDetail 中手写的 window.scrollTo hack）
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    if (to.name === 'map' && from.name === 'mapDetail') return false
    return { top: 0 }
  },
})

// 页面标题统一管理
const titles: Record<string, string> = {
  map: '地图资源',
  mapDetail: '地图详情',
  activity: '活动',
  announcement: '公告/关于',
  settings: '网站设置',
}

router.afterEach((to) => {
  const name = to.name as string
  const title = titles[name] ?? ''
  document.title = title ? `${title} · SDS Map Share` : 'SDS Map Share'
})

export default router
