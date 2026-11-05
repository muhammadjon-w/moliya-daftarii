import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router"

export type TabName = "dash" | "income" | "expense" | "plan" | "year" | "debts" | "report"

declare module "vue-router" {
  interface RouteMeta {
    tab?: TabName
    /** Ilova sarlavhasisiz alohida sahifa (to'lov sayti) */
    standalone?: boolean
  }
}

const Ledger = () => import("@/presentation/views/LedgerView.vue")

const routes: RouteRecordRaw[] = [
  { path: "/", name: "dash", component: Ledger, meta: { tab: "dash" } },
  { path: "/income", name: "income", component: Ledger, meta: { tab: "income" } },
  { path: "/expense", name: "expense", component: Ledger, meta: { tab: "expense" } },
  { path: "/plan", name: "plan", component: () => import("@/presentation/views/PlanView.vue"), meta: { tab: "plan" } },
  { path: "/year", name: "year", component: () => import("@/presentation/views/YearView.vue"), meta: { tab: "year" } },
  { path: "/debts", name: "debts", component: () => import("@/presentation/views/DebtsView.vue"), meta: { tab: "debts" } },
  { path: "/report", name: "report", component: () => import("@/presentation/views/ReportView.vue"), meta: { tab: "report" } },
  { path: "/obuna", name: "subscribe", component: () => import("@/presentation/views/SubscribeView.vue"), meta: { standalone: true } },
  { path: "/:pathMatch(.*)*", redirect: "/" },
]

export const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})
