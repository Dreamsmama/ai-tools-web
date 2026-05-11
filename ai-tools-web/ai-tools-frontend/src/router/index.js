import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ChatSummary from '../views/ChatSummary.vue'
import MedicalForm from '../views/MedicalForm.vue'
import MedicalResult from '../views/MedicalResult.vue'
import RagWorkbench from '../views/RagWorkbench.vue'
import RagUploadAsk from '../views/RagUploadAsk.vue'
import RagOfficialAsk from '../views/RagOfficialAsk.vue'
import AnalyticsDashboard from '../views/AnalyticsDashboard.vue'
import ModelCompareView from '../views/ModelCompareView.vue'
import MemoryCompareView from '../views/MemoryCompareView.vue'
import OfferDecisionView from '../views/OfferDecisionView.vue'
import XiaohongshuAgentView from '../views/XiaohongshuAgentView.vue'
import CareerTestPage from '../views/CareerTestPage.vue'
import CareerLibraryPage from '../views/CareerLibraryPage.vue'
import CareerDetailPage from '../views/CareerDetailPage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/career-test', name: 'careerTest', component: CareerTestPage },
    { path: '/career-library', name: 'careerLibrary', component: CareerLibraryPage },
    { path: '/career/:id', name: 'careerDetail', component: CareerDetailPage },
    { path: '/summary', name: 'summary', component: ChatSummary },
    { path: '/medical', name: 'medical', component: MedicalForm },
    { path: '/medical/result', name: 'medicalResult', component: MedicalResult },
    { path: '/rag', name: 'ragWorkbench', component: RagWorkbench },
    { path: '/rag/upload', name: 'ragUploadAsk', component: RagUploadAsk },
    { path: '/rag/official', name: 'ragOfficialAsk', component: RagOfficialAsk },
    { path: '/analytics', name: 'analyticsDashboard', component: AnalyticsDashboard },
    { path: '/model-compare', name: 'modelCompare', component: ModelCompareView },
    { path: '/tools/memory-compare', name: 'memoryCompare', component: MemoryCompareView },
    { path: '/tools/offer-decision', name: 'offerDecision', component: OfferDecisionView },
    { path: '/xiaohongshu-agent', name: 'xiaohongshuAgent', component: XiaohongshuAgentView },
  ],
})

export default router
