import { createRouter, createWebHistory } from 'vue-router'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/compare' },
    { path: '/compare', component: () => import('@/views/CompareView.vue'), meta: { title: '同行对比' } },
    { path: '/company/:code', component: () => import('@/views/CompanyView.vue'), meta: { title: '公司分析' } },
    { path: '/data-quality', component: () => import('@/views/DataQualityView.vue'), meta: { title: '数据质量' } },
  ],
  scrollBehavior: () => ({ top: 0 }),
})

router.afterEach((to) => { document.title = `${String(to.meta.title)} · 企业财务深度分析` })
