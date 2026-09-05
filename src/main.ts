import './assets/main.css'
import 'mdui/mdui.css'   // ← 新增：MDUI 样式
import 'mdui'             // ← 新增：MDUI 组件库

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')