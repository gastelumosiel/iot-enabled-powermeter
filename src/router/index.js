import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import MonitorView from '../views/MonitorView.vue'
import AnalyticsView from '../views/AnalyticsView.vue'
import CfeView from '../views/CfeView.vue'
import DeviceAdminView from '../views/DeviceAdminView.vue'
import ProfileView from '../views/ProfileView.vue'
import MainLayout from '../components/layout/MainLayout.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/monitor' },
    { path: '/login', name: 'login', component: LoginView, meta: { public: true } },
    { path: '/register', name: 'register', component: RegisterView, meta: { public: true } },
    {
      path: '/',
      component: MainLayout,
      children: [
        { path: 'monitor', name: 'monitor', component: MonitorView },
        { path: 'analytics', name: 'analytics', component: AnalyticsView },
        { path: 'cfe', name: 'cfe', component: CfeView },
        { path: 'admin/devices', name: 'admin-devices', component: DeviceAdminView },
        { path: 'profile', name: 'profile', component: ProfileView },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/monitor' },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isAuthenticated) return '/login'
  if (to.meta.public && auth.isAuthenticated) return '/monitor'
  return true
})

export default router
