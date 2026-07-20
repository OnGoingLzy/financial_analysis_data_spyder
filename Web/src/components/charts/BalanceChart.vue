<script setup lang="ts">import ScaleGrowthChart from './ScaleGrowthChart.vue'; defineProps<{ rows: Array<{ name: string; value: number | null }>; title: string; description: string }>()</script>
<template><ScaleGrowthChart :rows="rows" :title="title" :description="description" /></template>
