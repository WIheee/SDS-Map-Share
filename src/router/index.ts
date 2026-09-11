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
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    return { top: 0 }
  },
})

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
