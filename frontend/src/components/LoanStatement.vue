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
import { defineProps } from "vue";

defineProps<{ id: string }>();

// TODO(candidate): fetch the statement for this loan, reconcile the postings
// into a running balance, and render it. getStatement(id) is in api/loans.ts.
</script>

<template>
  <h1>Loan #{{ id }} — statement</h1>
  <p><em>Not built yet — this is the Feature Slice.</em></p>
  <p><RouterLink to="/">← back to loans</RouterLink></p>
</template>
