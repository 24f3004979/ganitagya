import { createWebHistory, createRouter } from 'vue-router';
import Auth from '../views/Auth.vue';
import Home from '../views/Home.vue'
import Dashboard from '../views/Dashboard.vue'

// Added explicit TypeScript typing for routes
export const routes = [
  { path: '/auth', component: Auth },
  { path: '/', component: Home },
  { path: '/dashboard', component: Dashboard }
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});

