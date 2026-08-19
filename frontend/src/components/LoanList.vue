<script setup lang="ts">
import { onMounted, ref } from "vue";
import { listLoans } from "../api/loans";
import { formatMoney } from "../money";
import type { LoanSummary } from "../types";

const loans = ref<LoanSummary[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);

onMounted(async () => {
  try {
    loans.value = await listLoans();
  } catch (e) {
    error.value = (e as Error).message;
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <h1>Loans</h1>
  <p v-if="loading">Loading…</p>
  <p v-else-if="error" class="error">{{ error }}</p>
  <table v-else>
    <thead>
      <tr>
        <th>Borrower</th>
        <th>Principal</th>
        <th>Rate</th>
        <th>Outstanding</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="loan in loans" :key="loan.id">
        <td>{{ loan.borrower }}</td>
        <td>{{ formatMoney(loan.principal) }}</td>
        <td>{{ loan.annual_rate }}</td>
        <td>{{ formatMoney(loan.outstanding) }}</td>
        <td><RouterLink :to="`/loans/${loan.id}`">Statement</RouterLink></td>
      </tr>
    </tbody>
  </table>
</template>

<style scoped>
.error { color: #b91c1c; }
</style>
