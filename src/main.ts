import './assets/main.css'
import 'mdui/mdui.css'
import 'mdui'
import { setTheme } from 'mdui/functions/setTheme.js'
import { setColorScheme } from 'mdui/functions/setColorScheme.js'
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import {
  colorPresets,
  STORAGE_KEYS,
  safeGetItem,
  type Theme,
  type ColorPreset,
} from './constants/theme'

// ── 在首帧渲染前同步应用已保存的主题，避免深色用户首屏白闪（FOUC）──
const savedTheme = safeGetItem(STORAGE_KEYS.theme) as Theme | null
if (savedTheme) setTheme(savedTheme)

const savedColor = safeGetItem(STORAGE_KEYS.colorScheme) as ColorPreset | null
if (savedColor && savedColor in colorPresets) {
  setColorScheme(colorPresets[savedColor])
}

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
