<template>
  <div class="about-page">
    <div class="header">
      <mdui-icon name="info" class="header-icon" aria-hidden="true"></mdui-icon>
      <h1>公告与关于</h1>
    </div>

    <!-- 公告卡片 -->
    <mdui-card class="info-card">
      <div class="card-header">
        <mdui-icon name="announcement" class="card-icon"></mdui-icon>
        <span>公告</span>
      </div>
      <mdui-divider></mdui-divider>
      <div class="card-body">欢迎使用 SDS 地图分享平台！当前版本为 v1.0，更多功能即将上线。</div>
    </mdui-card>

    <!-- 开源信息卡片 -->
    <mdui-card class="info-card">
      <div class="card-header">
        <mdui-icon name="code" class="card-icon"></mdui-icon>
        <span>开源协议</span>
      </div>
      <mdui-divider></mdui-divider>
      <div class="card-body">
        <p>该网站是开源的，并且遵循 <strong>GPL-3.0</strong> 开源协议。</p>
        <p style="margin-top: 8px">
          开源地址：
          <a
            href="https://github.com/WIheee/SDS-Map-Share"
            target="_blank"
            rel="noopener noreferrer"
            class="repo-link"
          >
            https://github.com/WIheee/SDS-Map-Share
          </a>
        </p>
      </div>
    </mdui-card>

    <!-- 团队卡片 -->
    <mdui-card class="info-card">
      <div class="card-header">
        <mdui-icon name="group" class="card-icon"></mdui-icon>
        <span>我们的团队</span>
      </div>
      <mdui-divider></mdui-divider>
      <div class="team-grid">
        <div v-for="member in team" :key="member.name" class="team-member">
          <img :src="member.avatar" :alt="member.name" class="avatar" loading="lazy" />
          <div class="member-info">
            <div class="member-name">{{ member.name }}</div>
            <div class="member-role">{{ member.role }}</div>
          </div>
        </div>
      </div>
    </mdui-card>
  </div>
</template>

<script setup lang="ts">
import 'mdui/components/card.js'
import 'mdui/components/icon.js'
import 'mdui/components/divider.js'

interface TeamMember {
  name: string
  role: string
  avatar: string
}

const team: TeamMember[] = [
  {
    name: 'WIheee',
    role: '首席开发者/维护者',
    avatar: '/team/WIhee.webp',
  },
]
</script>

<style scoped>
.about-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 800px;
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

.info-card {
  padding: 16px;
  margin-bottom: 16px;
  width: 100%;
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

.repo-link {
  color: rgb(var(--mdui-color-primary));
  text-decoration: none;
  word-break: break-all;
}
.repo-link:hover {
  text-decoration: underline;
}

.team-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
  padding-top: 12px;
}

.team-member {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 12px;
  background: rgb(var(--mdui-color-surface));
  border-radius: 8px;
  transition: transform 0.2s ease;
}
.team-member:hover {
  transform: translateY(-2px);
}

.avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: 8px;
  background: rgb(var(--mdui-color-surface-container));
}

.member-name {
  font-weight: 500;
  color: rgb(var(--mdui-color-on-surface));
  font-size: 16px;
}
.member-role {
  font-size: 12px;
  color: rgb(var(--mdui-color-on-surface-variant));
  margin-top: 4px;
}

@media (max-width: 600px) {
  .header-icon {
    font-size: 26px;
  }
  h1 {
    font-size: 20px;
  }
  .team-grid {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
