import Vue from 'vue';
import VueRouter from 'vue-router';
import axios from 'axios';

Vue.prototype.$axios = axios;
const apiRootPath = process.env.NODE_ENV !== 'production' ? 'http://localhost:8000/api/' : '/api/';
Vue.prototype.$apiRootPath = apiRootPath;
axios.defaults.baseURL = apiRootPath;

/* eslint-disable */
axios.interceptors.request.use((config) => {
  config.headers.AccessToken = localStorage.getItem('accessToken');
  return config;
}, (error) => Promise.reject(error));


Vue.use(VueRouter);

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
  },
  {
    path: '/favorite',
    name: 'Favorite',
    component: () => import('../views/Favorite.vue'),
  },
  {
    path: '/recent',
    name: 'Recent',
    component: () => import('../views/Recent.vue'),
  },
  {
    path: '/bin',
    name: 'RecycleBin',
    component: () => import('../views/RecycleBin.vue'),
  },
];

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes,
});

export default router;
