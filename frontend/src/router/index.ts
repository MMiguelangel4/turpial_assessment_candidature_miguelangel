import { createRouter, createWebHistory } from "vue-router";
import LoanList from "../components/LoanList.vue";
import LoanStatement from "../components/LoanStatement.vue";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "loans", component: LoanList },
    { path: "/loans/:id", name: "statement", component: LoanStatement, props: true },
  ],
});
