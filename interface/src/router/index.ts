import { createWebHistory, createRouter } from 'vue-router';
import Auth from '../views/Auth.vue';

// Added explicit TypeScript typing for routes
export const routes = [
  { path: '/auth', component: Auth },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});

