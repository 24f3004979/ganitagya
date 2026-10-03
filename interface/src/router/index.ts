import { createWebHistory, createRouter } from 'vue-router';
import Auth from '../views/Auth.vue';
import Home from '../views/Home.vue'
import Dashboard from '../views/Dashboard.vue'
import Logout from '../views/Logout.vue'

// Added explicit TypeScript typing for routes
export const routes = [
  { path: '/auth', component: Auth },
  { path: '/', component: Home },
  { path: '/dashboard', component: Dashboard },
  { path: '/logout', component: Logout }
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});

