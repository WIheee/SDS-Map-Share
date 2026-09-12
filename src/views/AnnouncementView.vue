<template>
  <div class="about-page">
    <div class="header">
      <mdui-icon name="info" class="header-icon" aria-hidden="true"></mdui-icon>
      <h1>{{ t('announcement.title') }}</h1>
    </div>

    <!-- 公告 -->
    <mdui-card class="info-card">
      <div class="card-header">
        <mdui-icon name="announcement" class="card-icon"></mdui-icon>
        <span>{{ t('announcement.announcement') }}</span>
      </div>
      <mdui-divider></mdui-divider>
      <div class="card-body">{{ t('announcement.announcementContent') }}</div>
    </mdui-card>

    <!-- 开源协议 -->
    <mdui-card class="info-card">
      <div class="card-header">
        <mdui-icon name="code" class="card-icon"></mdui-icon>
        <span>{{ t('announcement.license') }}</span>
      </div>
      <mdui-divider></mdui-divider>
      <div class="card-body">
        <p>{{ t('announcement.licenseContent') }}</p>
        <p style="margin-top: 8px">
          {{ t('announcement.repoAddress') }}
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

    <!-- 团队 -->
    <mdui-card class="info-card">
      <div class="card-header">
        <mdui-icon name="group" class="card-icon"></mdui-icon>
        <span>{{ t('announcement.team') }}</span>
      </div>
      <mdui-divider></mdui-divider>
      <div class="team-grid">
        <div v-for="member in team" :key="member.name" class="team-member">
          <img :src="member.avatar" :alt="member.name" class="avatar" loading="lazy" />
          <div class="member-info">
            <div class="member-name">
              <a
                v-if="member.github"
                :href="member.github"
                target="_blank"
                rel="noopener noreferrer"
                class="github-link"
              >
                {{ member.name }}
              </a>
              <span v-else>{{ member.name }}</span>
            </div>
            <div class="member-role">{{ member.role }}</div>
          </div>
        </div>
      </div>
    </mdui-card>

    <!-- 邮箱 -->
    <mdui-card class="info-card">
      <div class="card-header">
        <mdui-icon name="mail" class="card-icon"></mdui-icon>
        <span>{{ t('announcement.email') }}</span>
      </div>
      <mdui-divider></mdui-divider>
      <div class="card-body email-body">
        <p>{{ t('announcement.emailDesc') }}</p>
        <a :href="emailHref" class="email-link">
          <mdui-icon name="mail" class="email-icon"></mdui-icon>
          {{ EMAIL }}
        </a>
      </div>
    </mdui-card>

    <!-- Discord 社区 -->
    <mdui-card class="info-card">
      <div class="card-header">
        <mdui-icon name="forum" class="card-icon"></mdui-icon>
        <span>{{ t('announcement.discord') }}</span>
      </div>
      <mdui-divider></mdui-divider>
      <div class="card-body discord-body">
        <p>{{ t('announcement.discordDesc') }}</p>
        <mdui-button variant="filled" icon="forum" class="discord-btn" @click="openDiscord">
          {{ t('announcement.discordButton') }}
        </mdui-button>
      </div>
    </mdui-card>

    <!-- QQ 群 -->
    <mdui-card class="info-card">
      <div class="card-header">
        <mdui-icon name="group_add" class="card-icon"></mdui-icon>
        <span>{{ t('announcement.joinGroup') }}</span>
      </div>
      <mdui-divider></mdui-divider>
      <div class="card-body join-group-body">
        <p>{{ t('announcement.joinGroupDesc') }}</p>
        <mdui-button variant="filled" icon="group_add" class="join-group-btn" @click="openGroup">
          {{ t('announcement.joinGroupButton') }}
        </mdui-button>
      </div>
    </mdui-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import 'mdui/components/card.js'
import 'mdui/components/icon.js'
import 'mdui/components/divider.js'
import 'mdui/components/button.js'

const { t } = useI18n()

// ⚠️ 邮箱地址
const EMAIL = 'bywihee@outlook.com'

// QQ 群邀请链接
const GROUP_URL =
  'https://qun.qq.com/universal-share/share?ac=1&authKey=vACL5aGiSRKwNdk9PQpevQe3l%2BoYxn5CSXaqQIVEDjBVuWRUI8DsXvwSYJPKAPmo&busi_data=eyJncm91cENvZGUiOiI5OTEyNDAyNzAiLCJ0b2tlbiI6IjdHLzNJYlFZNzJRNG5yQ2VjcmlEOVVhQ05yemdpN0FJd3hTZDBpQjJyTjBueWNOS29PWTFiUy8rc1dNU1RpWkgiLCJ1aW4iOiIzMjg5NTc1ODIxIn0%3D&data=alw3G_blKFAMNyum3E8A4tHd5PuPThsX1izuO1qT-YLTsUFD1nQcjcyU0lTkOLgP0TF8JUqqZtqaj0UpODYz8Q&svctype=4&tempid=h5_group_info'

// Discord 社区链接
const DISCORD_URL = 'https://discord.gg/FeGk8JF4py'

// 邮件链接：主题和正文从 i18n 读取，切换语言时自动跟随
const emailHref = computed(() => {
  const subject = t('announcement.emailSubject')
  const body = t('announcement.emailBody')
  return `mailto:${EMAIL}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`
})

const openGroup = () => {
  window.open(GROUP_URL, '_blank', 'noopener,noreferrer')
}

const openDiscord = () => {
  window.open(DISCORD_URL, '_blank', 'noopener,noreferrer')
}

interface TeamMember {
  name: string
  role: string
  avatar: string
  github?: string
}

const team: TeamMember[] = [
  {
    name: 'WIhee',
    role: '首席开发者/维护者/地图管理员',
    avatar: '/team/WIhee.webp',
    github: 'https://github.com/WIheee',
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
  white-space: pre-line;
}

.repo-link {
  color: rgb(var(--mdui-color-primary));
  text-decoration: none;
  word-break: break-all;
}
.repo-link:hover {
  text-decoration: underline;
}

/* 团队 */
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
  font-size: 16px;
  color: rgb(var(--mdui-color-on-surface));
}

.github-link {
  color: rgb(var(--mdui-color-primary));
  text-decoration: none;
}
.github-link:hover {
  text-decoration: underline;
}

.member-role {
  font-size: 12px;
  color: rgb(var(--mdui-color-on-surface-variant));
  margin-top: 4px;
}

/* 邮箱 */
.email-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.email-body p {
  margin: 0;
  color: rgb(var(--mdui-color-on-surface-variant));
  font-size: 14px;
  line-height: 1.6;
}

.email-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: rgb(var(--mdui-color-primary));
  text-decoration: none;
  font-size: 16px;
  font-weight: 500;
  word-break: break-all;
  align-self: flex-start;
  transition: color 0.2s ease;
}

.email-link:hover {
  text-decoration: underline;
}

.email-icon {
  font-size: 20px;
  flex-shrink: 0;
}

/* Discord */
.discord-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.discord-body p {
  margin: 0;
  color: rgb(var(--mdui-color-on-surface-variant));
  font-size: 14px;
  line-height: 1.6;
}

.discord-btn {
  align-self: flex-start;
  --mdui-button-container-color: rgb(var(--mdui-color-primary));
  --mdui-button-label-text-color: rgb(var(--mdui-color-on-primary));
}

/* QQ 群 */
.join-group-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.join-group-body p {
  margin: 0;
  color: rgb(var(--mdui-color-on-surface-variant));
  font-size: 14px;
  line-height: 1.6;
}

.join-group-btn {
  align-self: flex-start;
  --mdui-button-container-color: rgb(var(--mdui-color-primary));
  --mdui-button-label-text-color: rgb(var(--mdui-color-on-primary));
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
  .email-link,
  .discord-btn,
  .join-group-btn {
    align-self: stretch;
  }
}
</style>
