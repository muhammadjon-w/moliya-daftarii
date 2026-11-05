import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router"
import { ROUTES } from "@/constants/routes"

declare module "vue-router" {
  interface RouteMeta {
    /** Pastki navigatsiyasiz alohida sahifa (to'lov sayti). */
    standalone?: boolean
  }
}

const routes: RouteRecordRaw[] = [
  { path: "/", name: ROUTES.home, component: () => import("@/pages/HomePage.vue") },
  { path: "/records", name: ROUTES.records, component: () => import("@/pages/RecordsPage.vue") },
  { path: "/report", name: ROUTES.report, component: () => import("@/pages/ReportPage.vue") },
  { path: "/debts", name: ROUTES.debts, component: () => import("@/pages/DebtsPage.vue") },
  { path: "/plan", name: ROUTES.plan, component: () => import("@/pages/PlanPage.vue") },
  { path: "/obuna", name: ROUTES.subscribe, component: () => import("@/pages/SubscribePage.vue"), meta: { standalone: true } },
  { path: "/:pathMatch(.*)*", redirect: "/" },
]

export const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})
