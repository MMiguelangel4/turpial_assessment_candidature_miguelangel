<script setup lang="ts">
/*
  ┌─────────────────────────────────────────────────────────────────────┐
  │  THIS IS YOUR TASK (front-end Feature Slice).                        │
  │                                                                     │
  │  Build the loan statement view. Given a loan, show its statement:    │
  │  the running balance as it changes over the loan's history,          │
  │  reconciled from the accounting records the API exposes at           │
  │  GET /api/loans/:id/statement/  (an ordered list of transactions,    │
  │  each with signed postings).                                        │
  │                                                                     │
  │  Routing, data fetching, and the component patterns you'll follow    │
  │  are already here — see LoanList.vue and api/loans.ts.               │
  │                                                                     │
  │  You decide what a useful statement looks like and how it behaves    │
  │  when the numbers don't line up — because sometimes they won't.      │
  │  Read GLOSSARY.md first.                                             │
  └─────────────────────────────────────────────────────────────────────┘
*/
import { computed, onMounted, ref, watch } from "vue";
import { getLoan, getStatement } from "../api/loans";
import { formatMoney, formatSigned } from "../money";
import { moneyEquals, reconcileStatement } from "../statement";
import type { LoanSummary } from "../types";
import type { ReconciledStatement } from "../statement";

const props = defineProps<{ id: string }>();

const loan = ref<LoanSummary | null>(null);
const statement = ref<ReconciledStatement | null>(null);
const loading = ref(true);
const error = ref<string | null>(null);

const loanId = computed(() => Number(props.id));

const mismatch = computed(() => {
  if (!loan.value || !statement.value) return false;
  return !moneyEquals(loan.value.outstanding, statement.value.derivedOutstanding);
});

async function load() {
  loading.value = true;
  error.value = null;
  loan.value = null;
  statement.value = null;
  try {
    const [loanData, lines] = await Promise.all([
      getLoan(loanId.value),
      getStatement(loanId.value),
    ]);
    loan.value = loanData;
    statement.value = reconcileStatement(lines);
  } catch (e) {
    error.value = (e as Error).message;
  } finally {
    loading.value = false;
  }
}

onMounted(load);
watch(() => props.id, load);

function kindLabel(kind: string): string {
  return kind.replace(/_receivable$/, "").replace(/_/g, " ");
}
</script>

<template>
  <p><RouterLink to="/">← back to loans</RouterLink></p>

  <p v-if="loading">Loading…</p>
  <p v-else-if="error" class="error">{{ error }}</p>

  <template v-else-if="loan && statement">
    <h1>Loan #{{ loan.id }} — statement</h1>
    <p class="meta">
      {{ loan.borrower }} · opened {{ loan.opened_on }} · rate {{ loan.annual_rate }}
    </p>

    <dl class="summary">
      <div>
        <dt>Principal</dt>
        <dd>{{ formatMoney(loan.principal) }}</dd>
      </div>
      <div>
        <dt>Fees (opening)</dt>
        <dd>{{ formatMoney(loan.fees) }}</dd>
      </div>
      <div>
        <dt>Outstanding (API cache)</dt>
        <dd>{{ formatMoney(loan.outstanding) }}</dd>
      </div>
      <div>
        <dt>Outstanding (from statement)</dt>
        <dd>{{ formatMoney(statement.derivedOutstanding) }}</dd>
      </div>
    </dl>

    <p v-if="mismatch" class="warn">
      The cached outstanding ({{ formatMoney(loan.outstanding) }}) does not match
      the balance derived from this statement
      ({{ formatMoney(statement.derivedOutstanding) }}).
      The statement is built from postings; the list/detail field uses cached
      account balances.
    </p>

    <p v-if="!statement.allBalanced" class="warn">
      At least one transaction has postings that do not sum to zero
      (double-entry broken). Those rows are marked below.
    </p>

    <table v-if="statement.rows.length">
      <thead>
        <tr>
          <th>Date</th>
          <th>Memo</th>
          <th>Change</th>
          <th>Running balance</th>
          <th>Postings</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="row in statement.rows"
          :key="row.id"
          :class="{ unbalanced: !row.balanced }"
        >
          <td>{{ row.effective_on }}</td>
          <td>
            {{ row.memo || "—" }}
            <span v-if="!row.balanced" class="badge">unbalanced</span>
          </td>
          <td>{{ formatSigned(row.delta) }}</td>
          <td>{{ formatMoney(row.balance) }}</td>
          <td>
            <ul class="postings">
              <li v-for="p in row.postings" :key="p.id">
                {{ kindLabel(p.account_kind) }}:
                {{ formatSigned(p.amount) }}
              </li>
            </ul>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-else>No transactions on this loan yet.</p>
  </template>
</template>

<style scoped>
.error { color: #b91c1c; }
.warn {
  background: #fff7ed;
  border-left: 3px solid #ea580c;
  padding: 10px 14px;
  color: #9a3412;
}
.meta { color: #525252; margin-top: -8px; }
.summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
  margin: 20px 0;
}
.summary dt { font-size: 12px; color: #737373; text-transform: uppercase; letter-spacing: 0.04em; }
.summary dd { margin: 4px 0 0; font-weight: 600; }
.postings { list-style: none; margin: 0; padding: 0; font-size: 13px; color: #525252; }
.unbalanced { background: #fef2f2; }
.badge {
  display: inline-block;
  margin-left: 6px;
  font-size: 11px;
  color: #b91c1c;
  font-weight: 600;
  text-transform: uppercase;
}
</style>
