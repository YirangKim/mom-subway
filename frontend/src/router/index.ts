import {createRouter, createWebHistory} from "vue-router";

import SplashView from "../views/SplashView.vue";
import HomeView from "../views/HomeView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "splash",
      component: SplashView,
    },
    {
      path: "/main",
      name: "main",
      component: HomeView,
    },
  ],
});

export default router;
