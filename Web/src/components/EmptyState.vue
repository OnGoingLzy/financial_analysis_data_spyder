<script setup lang="ts">defineProps<{ title: string; description: string }>()</script>
<template><div class="empty panel"><p class="terminal-meta">NO DATA</p><h2>{{ title }}</h2><p>{{ description }}</p></div></template>
<style scoped>.empty { padding: var(--space-xl); }.empty h2 { font-size: var(--text-lg); }.empty p:last-child { margin: 0; color: var(--color-ink-muted); }</style>
