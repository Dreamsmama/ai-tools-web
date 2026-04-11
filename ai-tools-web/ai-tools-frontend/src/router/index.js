import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ChatSummary from '../views/ChatSummary.vue'
import MedicalForm from '../views/MedicalForm.vue'
import MedicalResult from '../views/MedicalResult.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/summary', name: 'summary', component: ChatSummary },
    { path: '/medical', name: 'medical', component: MedicalForm },
    { path: '/medical/result', name: 'medicalResult', component: MedicalResult },
  ],
})

export default router
