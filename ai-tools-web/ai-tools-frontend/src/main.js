import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { setupRouteAnalytics } from './analytics'
import './style.css'

setupRouteAnalytics(router)
createApp(App).use(router).mount('#app')
