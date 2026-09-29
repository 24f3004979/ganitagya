import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/quiz' },
    { path: '/login', component: () => import('../views/LoginView.vue'), meta: { guestOnly: true } },
    { path: '/register', component: () => import('../views/RegisterView.vue'), meta: { guestOnly: true } },
    { path: '/quiz', component: () => import('../views/QuizView.vue'), meta: { requiresAuth: true } }
    // Add your Chintan page here, e.g. { path: '/chintan', component: () => import('../views/ChintanView.vue') }
  ]
})

router.beforeEach((to) => {
  const { isLoggedIn } = useAuth()
  if (to.meta.requiresAuth && !isLoggedIn.value) return { path: '/login', query: { redirect: to.fullPath } }
  if (to.meta.guestOnly && isLoggedIn.value) return '/quiz'
})

export default router
