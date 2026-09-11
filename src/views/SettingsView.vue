<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { setTheme } from 'mdui/functions/setTheme.js'
import { setColorScheme } from 'mdui/functions/setColorScheme.js'
import {
  colorPresets,
  STORAGE_KEYS,
  safeGetItem,
  safeSetItem,
  safeRemoveItem,
  type Theme,
  type ColorPreset,
} from '@/constants/theme'
import { setLocale as setI18nLocale } from '@/i18n'
import 'mdui/components/segmented-button-group.js'
import 'mdui/components/segmented-button.js'
import 'mdui/components/select.js'
import 'mdui/components/menu-item.js'
import 'mdui/components/icon.js'
import 'mdui/components/text-field.js'
import 'mdui/components/dialog.js'
import 'mdui/components/button-icon.js'

defineOptions({ name: 'SettingsPage' })

const { t, locale } = useI18n()

const theme = ref<Theme>((safeGetItem(STORAGE_KEYS.theme) as Theme | null) || 'auto')

const savedColorScheme = safeGetItem(STORAGE_KEYS.colorScheme) as ColorPreset | null
const currentColor = ref<string>(
  safeGetItem(STORAGE_KEYS.customColor) ||
    (savedColorScheme && colorPresets[savedColorScheme]) ||
    colorPresets.purple,
)

const matchedPreset = computed<ColorPreset | null>(() => {
  for (const [preset, hex] of Object.entries(colorPresets)) {
    if (hex.toLowerCase() === currentColor.value.toLowerCase()) {
      return preset as ColorPreset
    }
  }
  return null
})

const isCustom = computed(() => matchedPreset.value === null)

// ---- 对话框状态 ----
const colorDialogOpen = ref(false)
const dialogInput = ref('')
const dialogError = ref('')

// 对话框中的实时预览颜色
const dialogPreviewColor = computed(() => {
  const raw = dialogInput.value.trim()
  if (!raw) return currentColor.value
  const normalized = normalizeHex(raw)
  return isValidHex(normalized) ? normalized : currentColor.value
})

const languageOptions = [
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

function isValidHex(value: string): boolean {
  return /^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})$/.test(value)
}

function normalizeHex(value: string): string {
  let v = value.trim()
  if (!v.startsWith('#')) v = '#' + v
  if (/^#[0-9A-Fa-f]{3}$/.test(v)) {
    const [r, g, b] = v.slice(1).split('')
    v = `#${r}${r}${g}${g}${b}${b}`
  }
  return v
}

const applyColor = (hex: string, preset?: ColorPreset) => {
  currentColor.value = hex
  setColorScheme(hex)
  if (preset) {
    safeSetItem(STORAGE_KEYS.colorScheme, preset)
    safeRemoveItem(STORAGE_KEYS.customColor)
  } else {
    safeSetItem(STORAGE_KEYS.customColor, hex)
    safeRemoveItem(STORAGE_KEYS.colorScheme)
  }
}

const applyPresetColor = (preset: ColorPreset) => {
  applyColor(colorPresets[preset], preset)
}

// ---- 打开 / 取消 / 确定 ----
const openColorDialog = () => {
  dialogInput.value = currentColor.value
  dialogError.value = ''
  colorDialogOpen.value = true
}

const cancelDialog = () => {
  colorDialogOpen.value = false
}

const confirmDialog = () => {
  const raw = dialogInput.value.trim()
  if (!raw) {
    dialogError.value = t('settings.invalidHex')
    return
  }
  const normalized = normalizeHex(raw)
  if (!isValidHex(normalized)) {
    dialogError.value = t('settings.invalidHex')
    return
  }
  applyColor(normalized)
  colorDialogOpen.value = false
}

// 实时校验
watch(dialogInput, (val) => {
  if (!val.trim()) {
    dialogError.value = ''
    return
  }
  const normalized = normalizeHex(val.trim())
  if (!isValidHex(normalized)) {
    dialogError.value = t('settings.invalidHex')
  } else {
    dialogError.value = ''
  }
})

const applyTheme = (value: Theme) => {
  theme.value = value
  setTheme(value)
  safeSetItem(STORAGE_KEYS.theme, value)
}

const onLanguageChange = async (event: Event) => {
  const target = event.target as HTMLSelectElement
  await setI18nLocale(target.value as never)
}

onMounted(() => {
  setTheme(theme.value)
  setColorScheme(currentColor.value)
})
</script>

<template>
  <div class="settings-page">
    <h1>{{ t('settings.title') }}</h1>

    <!-- 主题模式 -->
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

    <!-- 主题色 -->
    <div class="setting-section">
      <p>{{ t('settings.themeColor') }}</p>
      <div class="color-presets">
        <button
          v-for="(hex, preset) in colorPresets"
          :key="preset"
          class="color-dot"
          :class="{ active: matchedPreset === preset }"
          :style="{ backgroundColor: hex }"
          @click="applyPresetColor(preset as ColorPreset)"
          :aria-label="`切换到 ${preset} 主题`"
        ></button>

        <button
          class="color-dot color-dot-custom"
          :class="{ active: isCustom }"
          :style="{ backgroundColor: isCustom ? currentColor : '#FFFFFF' }"
          @click="openColorDialog"
          :aria-label="t('settings.customColor')"
          :title="t('settings.customColor')"
        >
          <mdui-icon name="colorize" class="custom-icon"></mdui-icon>
        </button>
      </div>
    </div>

    <!-- 语言 -->
    <div class="setting-section">
      <p>{{ t('settings.language') }}</p>
      <mdui-select
        :value="locale"
        @change="onLanguageChange"
        class="language-select"
        aria-label="Language"
      >
        <mdui-menu-item v-for="opt in languageOptions" :key="opt.value" :value="opt.value">
          {{ opt.label }}
        </mdui-menu-item>
      </mdui-select>
    </div>

    <!-- ==================== 自定义颜色对话框 ==================== -->
    <mdui-dialog
      :open="colorDialogOpen"
      :headline="t('settings.customColor')"
      @close="colorDialogOpen = false"
    >
      <div class="color-dialog-body">
        <mdui-text-field
          v-model="dialogInput"
          :label="t('settings.customColor')"
          placeholder="#39C5BB"
          clearable
          :error="!!dialogError"
          :helper="dialogError || t('settings.hexHelper')"
          @keydown.enter="confirmDialog"
        >
          <mdui-icon slot="icon" name="palette"></mdui-icon>
        </mdui-text-field>

        <div class="color-preview-row">
          <div class="color-preview-large" :style="{ backgroundColor: dialogPreviewColor }"></div>
          <span class="color-preview-text">{{ dialogPreviewColor.toUpperCase() }}</span>
        </div>
      </div>

      <!-- 图标按钮：X 取消 / √ 确定 -->
      <mdui-button-icon
        slot="action"
        icon="close"
        :aria-label="t('common.cancel')"
        :title="t('common.cancel')"
        @click="cancelDialog"
      ></mdui-button-icon>
      <mdui-button-icon
        slot="action"
        icon="check"
        :aria-label="t('common.confirm')"
        :title="t('common.confirm')"
        @click="confirmDialog"
      ></mdui-button-icon>
    </mdui-dialog>
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
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.color-dot:hover {
  transform: scale(1.1);
}

.color-dot.active {
  border-color: rgb(var(--mdui-color-on-surface));
  box-shadow: 0 0 0 2px rgb(var(--mdui-color-surface));
}

.color-dot-custom {
  border: 3px solid rgb(var(--mdui-color-outline-variant));
}

.color-dot-custom.active {
  border-color: rgb(var(--mdui-color-on-surface));
}

.custom-icon {
  font-size: 20px;
  pointer-events: none;
  color: #000;
  opacity: 0.6;
}

/* ===== 对话框内部样式 ===== */
.color-dialog-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 8px 0;
  width: 100%;
}

.color-preview-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.color-preview-large {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  border: 1px solid rgb(var(--mdui-color-outline-variant));
  flex-shrink: 0;
  transition: background-color 0.2s ease;
}

.color-preview-text {
  font-family: 'Roboto Mono', monospace;
  font-size: 16px;
  font-weight: 500;
  color: rgb(var(--mdui-color-on-surface-variant));
  letter-spacing: 0.05em;
}
</style>
