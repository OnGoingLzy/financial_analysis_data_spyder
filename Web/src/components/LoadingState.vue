<template><div class="loading panel" role="status"><span></span><p>正在读取标准化财务数据…</p></div></template>
<style scoped>
.loading { display: flex; align-items: center; gap: var(--space-sm); min-height: 7rem; padding: var(--space-xl); color: var(--color-ink-muted); }
.loading span { width: .65rem; height: .65rem; background: var(--color-accent); animation: pulse 1.2s var(--ease-in-out) infinite alternate; }
.loading p { margin: 0; }
@keyframes pulse { to { opacity: .28; transform: scale(.72); } }
</style>
