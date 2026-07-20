<template>
  <aside class="sidebar">
    <div class="brand">
      <span class="brand-mark">FA</span>
      <div><strong>FINANCIAL<br>ANALYSIS</strong><small>内部研究终端</small></div>
    </div>
    <nav aria-label="主要导航">
      <RouterLink to="/compare"><span>01</span><b>同行对比</b><small>横向基准与分位</small></RouterLink>
      <RouterLink to="/companies"><span>02</span><b>公司分析</b><small>查询公司后深入研究</small></RouterLink>
      <RouterLink to="/data-quality"><span>03</span><b>数据质量</b><small>来源、批次与异常</small></RouterLink>
    </nav>
    <div class="sidebar-foot"><span class="status-dot"></span><span>LOCAL / READ ONLY</span></div>
  </aside>
</template>

<style scoped>
.sidebar { position: fixed; inset: 0 auto 0 0; z-index: 10; display: flex; width: 15rem; flex-direction: column; border-right: var(--rule-thin) solid var(--color-rule); background: var(--color-paper-raised); }
.brand { display: flex; align-items: center; gap: var(--space-sm); min-height: 6rem; padding: var(--space-lg); border-bottom: var(--rule-thin) solid var(--color-rule); }
.brand-mark { display: grid; place-items: center; width: 2.25rem; height: 2.25rem; border: var(--rule-thin) solid var(--color-accent); color: var(--color-accent); font: 700 var(--text-sm) var(--font-data); }
.brand strong { display: block; font: 700 var(--text-sm)/1.25 var(--font-data); letter-spacing: .08em; }
.brand small { color: var(--color-ink-muted); font-size: var(--text-xs); }
nav { display: grid; padding-top: var(--space-md); }
nav a { position: relative; display: grid; grid-template-columns: 2rem 1fr; padding: var(--space-md) var(--space-lg); color: var(--color-ink-muted); white-space: nowrap; }
nav a::before { position: absolute; inset: 0 auto 0 0; width: 2px; content: ''; background: transparent; }
nav a:hover { color: var(--color-ink); background: var(--color-paper-overlay); }
nav a.router-link-active { color: var(--color-ink); background: var(--color-accent-wash); }
nav a.router-link-active::before { background: var(--color-accent); }
nav span { color: var(--color-ink-faint); font: var(--text-xs) var(--font-data); }
nav b { font-size: var(--text-sm); font-weight: 600; }
nav small { grid-column: 2; margin-top: var(--space-2xs); color: var(--color-ink-faint); font-size: var(--text-xs); }
.sidebar-foot { display: flex; align-items: center; gap: var(--space-xs); margin-top: auto; padding: var(--space-lg); border-top: var(--rule-thin) solid var(--color-rule); color: var(--color-ink-faint); font: var(--text-xs) var(--font-data); }
@media (max-width: 960px) { .sidebar { position: sticky; top: 0; width: 100%; height: auto; flex-direction: row; align-items: stretch; } .brand { min-height: 4rem; padding: var(--space-sm) var(--space-md); } .brand div { display: none; } nav { display: flex; flex: 1; justify-content: flex-end; padding: 0; } nav a { grid-template-columns: 1fr; place-items: center; padding: var(--space-sm); } nav span, nav small { display: none; } nav a::before { inset: auto 0 0 0; width: auto; height: 2px; } .sidebar-foot { display: none; } }
</style>
