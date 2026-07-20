<script setup lang="ts">defineProps<{ title: string; formula: string }>()</script>
<template><details class="formula-note"><summary>{{ title }}</summary><p>{{ formula }}</p></details></template>
<style scoped>.formula-note { border-top: var(--rule-thin) solid var(--color-rule); padding: var(--space-sm) var(--space-lg); color: var(--color-ink-muted); font-size: var(--text-xs); }.formula-note summary { cursor: pointer; color: var(--color-accent); }.formula-note p { margin: var(--space-xs) 0 0; font-family: var(--font-data); }</style>
