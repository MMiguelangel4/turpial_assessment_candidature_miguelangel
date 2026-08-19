<script setup lang="ts"></script>

<template>
  <header class="topbar">
    <RouterLink to="/" class="brand">Loan servicing</RouterLink>
  </header>
  <main class="wrap">
    <RouterView />
  </main>
</template>

<style>
:root { font-family: system-ui, sans-serif; color: #1a1a1a; }
body { margin: 0; background: #f6f6f4; }
.topbar { background: #0f0f0f; padding: 14px 24px; }
.brand { color: #fbd403; font-weight: 700; text-decoration: none; }
.wrap { max-width: 900px; margin: 0 auto; padding: 24px; }
table { border-collapse: collapse; width: 100%; }
th, td { text-align: left; padding: 8px 12px; border-bottom: 1px solid #e4e4e0; }
a { color: #2563eb; }
</style>
