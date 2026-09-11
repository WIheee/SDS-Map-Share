<template>
  <div class="activity-page">
    <div class="header">
      <mdui-icon name="event" class="header-icon" aria-hidden="true"></mdui-icon>
      <h1>{{ t('activity.title') }}</h1>
    </div>

    <div class="card-grid">
      <mdui-card v-for="activity in activities" :key="activity.id" class="activity-card">
        <div class="card-content">
          <h3>{{ activity.title }}</h3>
          <mdui-divider></mdui-divider>
          <p>{{ activity.description }}</p>
        </div>
      </mdui-card>
      <!-- 空状态预留：activities 目前由 i18n 提供固定占位数据，长度恒为 3；
           将来接入真实数据源（API / JSON）后可自然生效。 -->
      <div v-if="activities.length === 0" class="empty-state">
        <p>{{ t('activity.noActivities') }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import 'mdui/components/card.js'
import 'mdui/components/icon.js'
import 'mdui/components/divider.js'

const { t } = useI18n()

interface Activity {
  id: number
  title: string
  description: string
}

const activities = computed<Activity[]>(() => [
  { id: 1, title: t('activity.test1.title'), description: t('activity.test1.description') },
  { id: 2, title: t('activity.test2.title'), description: t('activity.test2.description') },
  { id: 3, title: t('activity.test3.title'), description: t('activity.test3.description') },
])
</script>

<style scoped>
.activity-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  box-sizing: border-box;
  min-height: calc(100vh - 160px);
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

.card-grid {
  display: grid;
  width: 100%;
  gap: 16px;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
}

.activity-card {
  overflow: hidden;
  background: rgb(var(--mdui-color-surface-container));
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}

.activity-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.card-content {
  padding: 16px;
}

.card-content h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: rgb(var(--mdui-color-on-surface));
}

.card-content p {
  margin: 8px 0 0 0;
  color: rgb(var(--mdui-color-on-surface-variant));
  font-size: 14px;
  line-height: 1.5;
}

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 48px 20px;
  color: rgb(var(--mdui-color-on-surface-variant));
}

@media (max-width: 600px) {
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
</style>
