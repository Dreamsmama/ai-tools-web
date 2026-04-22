import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ChatSummary from '../views/ChatSummary.vue'
import MedicalForm from '../views/MedicalForm.vue'
import MedicalResult from '../views/MedicalResult.vue'
import RagWorkbench from '../views/RagWorkbench.vue'
import RagUploadAsk from '../views/RagUploadAsk.vue'
import RagOfficialAsk from '../views/RagOfficialAsk.vue'
import AnalyticsDashboard from '../views/AnalyticsDashboard.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/summary', name: 'summary', component: ChatSummary },
    { path: '/medical', name: 'medical', component: MedicalForm },
    { path: '/medical/result', name: 'medicalResult', component: MedicalResult },
    { path: '/rag', name: 'ragWorkbench', component: RagWorkbench },
    { path: '/rag/upload', name: 'ragUploadAsk', component: RagUploadAsk },
    { path: '/rag/official', name: 'ragOfficialAsk', component: RagOfficialAsk },
    { path: '/analytics', name: 'analyticsDashboard', component: AnalyticsDashboard },
  ],
})

export default router
