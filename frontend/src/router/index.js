import Vue from 'vue';
import VueRouter from 'vue-router';
import Login from '../components/Login.vue';
import Portal from '../components/Portal.vue';

Vue.use(VueRouter);

const routes = [
  {
    path: '/portal',
    name: 'Portal',
    component: Portal,
  },
  {
    path: '/',
    name: 'Login',
    component: Login,
  },
];

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes,
});

export default router;
