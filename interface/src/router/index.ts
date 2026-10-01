import { createWebHistory, createRouter} from 'vue-router';
import HomeView from '../views/HomeView.vue';
import WaitList from '../views/WaitList.vue';

// Added explicit TypeScript typing for routes
export const routes = [
  { path: '/', component: HomeView },
  { path: '/login', component: WaitList },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});

