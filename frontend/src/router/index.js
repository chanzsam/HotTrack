import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import TopViewed from '../views/TopViewed.vue'
import Trending from '../views/Trending.vue'
import Viral from '../views/Viral.vue'
import Revenue from '../views/Revenue.vue'
import AiTools from '../views/AiTools.vue'
import Crawl from '../views/Crawl.vue'

const routes = [
  { path: '/', name: 'Dashboard', component: Dashboard },
  { path: '/top-viewed', name: 'TopViewed', component: TopViewed },
  { path: '/trending', name: 'Trending', component: Trending },
  { path: '/viral', name: 'Viral', component: Viral },
  { path: '/revenue', name: 'Revenue', component: Revenue },
  { path: '/ai-tools', name: 'AiTools', component: AiTools },
  { path: '/crawl', name: 'Crawl', component: Crawl },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
