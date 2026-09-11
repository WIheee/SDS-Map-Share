<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { setTheme } from 'mdui/functions/setTheme.js'
import { setColorScheme } from 'mdui/functions/setColorScheme.js'
import {
  colorPresets,
  STORAGE_KEYS,
  safeGetItem,
  safeSetItem,
  type Theme,
  type ColorPreset,
} from '@/constants/theme'
import { SUPPORT_LOCALES, setLocale as setI18nLocale } from '@/i18n'
import 'mdui/components/segmented-button-group.js'
import 'mdui/components/segmented-button.js'
import 'mdui/components/select.js'
import 'mdui/components/menu-item.js'
import 'mdui/components/icon.js'

defineOptions({ name: 'SettingsPage' })

const { t, locale } = useI18n()

const theme = ref<Theme>((safeGetItem(STORAGE_KEYS.theme) as Theme | null) || 'auto')
const currentColor = ref<ColorPreset>(
  (safeGetItem(STORAGE_KEYS.colorScheme) as ColorPreset | null) || 'purple',
)

const languageOptions: { value: string; label: string }[] = [
  { value: 'zh-CN', label: '简体中文' },
  { value: 'zh-TW', label: '繁體中文' },
  { value: 'en-US', label: 'English (US)' },
  { value: 'en-GB', label: 'English (UK)' },
  { value: 'ja', label: '日本語' },
  { value: 'ko', label: '한국어' },
  { value: 'fr', label: 'Français' },
  { value: 'de', label: 'Deutsch' },
  { value: 'es', label: 'Español' },
  { value: 'ru', label: 'Русский' },
]

const applyTheme = (value: Theme) => {
  theme.value = value
  setTheme(value)
  safeSetItem(STORAGE_KEYS.theme, value)
}

const applyColorScheme = (preset: ColorPreset) => {
  currentColor.value = preset
  setColorScheme(colorPresets[preset])
  safeSetItem(STORAGE_KEYS.colorScheme, preset)
}

const onLanguageChange = async (event: Event) => {
  const target = event.target as HTMLSelectElement
  const newLocale = target.value
  await setI18nLocale(newLocale as any)
}

onMounted(() => {
  setTheme(theme.value)
  setColorScheme(colorPresets[currentColor.value])
})
</script>

<template>
  <div class="settings-page">
    <h1>{{ t('settings.title') }}</h1>

    <div class="setting-section">
      <p>{{ t('settings.themeMode') }}</p>
      <mdui-segmented-button-group selects="single" required :value="theme">
        <mdui-segmented-button value="light" @click="applyTheme('light')">
          <mdui-icon name="light_mode" slot="icon"></mdui-icon>
          {{ t('settings.light') }}
        </mdui-segmented-button>
        <mdui-segmented-button value="dark" @click="applyTheme('dark')">
          <mdui-icon name="dark_mode" slot="icon"></mdui-icon>
          {{ t('settings.dark') }}
        </mdui-segmented-button>
        <mdui-segmented-button value="auto" @click="applyTheme('auto')">
          <mdui-icon name="brightness_auto" slot="icon"></mdui-icon>
          {{ t('settings.auto') }}
        </mdui-segmented-button>
      </mdui-segmented-button-group>
    </div>

    <div class="setting-section">
      <p>{{ t('settings.themeColor') }}</p>
      <div class="color-presets">
        <button
          v-for="preset in Object.keys(colorPresets) as ColorPreset[]"
          :key="preset"
          class="color-dot"
          :class="{ active: currentColor === preset }"
          :style="{ backgroundColor: colorPresets[preset] }"
          @click="applyColorScheme(preset)"
          :aria-label="`切换到 ${preset} 主题`"
        ></button>
      </div>
    </div>

    <div class="setting-section">
      <p>{{ t('settings.language') }}</p>
      <mdui-select
        :value="locale"
        @change="onLanguageChange"
        class="language-select"
        aria-label="Language"
      >
        <mdui-menu-item
          v-for="opt in languageOptions"
          :key="opt.value"
          :value="opt.value"
        >
          {{ opt.label }}
        </mdui-menu-item>
      </mdui-select>
    </div>
  </div>
</template>

<style scoped>
.settings-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
  padding: 40px 20px;
  box-sizing: border-box;
  min-height: calc(100vh - 160px);
  color: rgb(var(--mdui-color-on-surface));
}

h1 {
  text-align: center;
  font-size: 28px;
  margin-bottom: 32px;
  color: rgb(var(--mdui-color-on-surface));
}

.setting-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 28px;
  width: 100%;
}

.setting-section p {
  font-size: 14px;
  color: rgb(var(--mdui-color-on-surface-variant));
  margin: 0;
  text-align: center;
}

mdui-segmented-button-group {
  width: 100%;
}

.language-select {
  width: 100%;
}

.color-presets {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
}

.color-dot {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 3px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
}

.color-dot:hover {
  transform: scale(1.1);
}

.color-dot.active {
  border-color: rgb(var(--mdui-color-on-surface));
  box-shadow: 0 0 0 2px rgb(var(--mdui-color-surface));
}
</style>
