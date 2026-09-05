<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { setTheme } from 'mdui/functions/setTheme.js'
import { setColorScheme } from 'mdui/functions/setColorScheme.js'
import 'mdui/components/segmented-button-group.js'
import 'mdui/components/segmented-button.js'
import 'mdui/components/icon.js'

defineOptions({ name: 'SettingsPage' })

type Theme = 'light' | 'dark' | 'auto'
type ColorPreset = 'purple' | 'blue' | 'green' | 'pink'

const colorPresets: Record<ColorPreset, string> = {
  purple: '#6750A4',
  blue: '#0061A4',
  green: '#1E7A5E',
  pink: '#B93A6C'
}

const savedTheme = localStorage.getItem('theme') as Theme | null
const theme = ref<Theme>(savedTheme || 'auto')

const savedColor = localStorage.getItem('colorScheme') as ColorPreset | null
const currentColor = ref<ColorPreset>(savedColor || 'purple')

const applyTheme = (value: Theme) => {
  theme.value = value
  setTheme(value)
  localStorage.setItem('theme', value)
}

const applyColorScheme = (preset: ColorPreset) => {
  currentColor.value = preset
  setColorScheme(colorPresets[preset])
  localStorage.setItem('colorScheme', preset)
}

onMounted(() => {
  setTheme(theme.value)
  setColorScheme(colorPresets[currentColor.value])
})
</script>

<template>
  <div class="settings-page">
    <h1>设置</h1>

    <div class="setting-section">
      <p>主题模式</p>
      <mdui-segmented-button-group
        selects="single"
        required
        :value="theme"
      >
        <mdui-segmented-button value="light" @click="applyTheme('light')">
          <mdui-icon name="light_mode" slot="icon"></mdui-icon>
          浅色
        </mdui-segmented-button>
        <mdui-segmented-button value="dark" @click="applyTheme('dark')">
          <mdui-icon name="dark_mode" slot="icon"></mdui-icon>
          深色
        </mdui-segmented-button>
        <mdui-segmented-button value="auto" @click="applyTheme('auto')">
          <mdui-icon name="brightness_auto" slot="icon"></mdui-icon>
          自动
        </mdui-segmented-button>
      </mdui-segmented-button-group>
    </div>

    <div class="setting-section">
      <p>主题色</p>
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
  </div>
</template>

<style scoped>
.settings-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
  padding: 40px 20px;
  color: rgb(var(--mdui-color-on-surface));
  box-sizing: border-box;
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
