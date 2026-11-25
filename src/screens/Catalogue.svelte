<script lang="ts">
  import Icon from '../components/Icon.svelte';
  import Toggle from '../components/Toggle.svelte';
  import { t, fmt } from '../lib/i18n/index.svelte';
  import { catalog, type Category } from '../lib/state/catalog.svelte';
  import { session } from '../lib/state/session.svelte';
  import { ui } from '../lib/state/ui.svelte';

  const id = $props.id();
  catalog.load();

  const shown = $derived(catalog.filtered.slice(0, catalog.limit));
  const cats: ('all' | Category)[] = ['all', 'sans', 'serif', 'display', 'hand', 'mono'];
  const sample = $derived(t('gf.sample'));

  // Aperçus : la feuille Google Fonts de chaque carte visible, limitée aux lettres affichées.
  const loaded = new Set<string>();
  function preview(node: HTMLElement, family: string) {
    const io = new IntersectionObserver((entries) => {
      if (!entries.some((e) => e.isIntersecting)) return;
      io.disconnect();
      const f = catalog.families.find((x) => x.family === family);
      if (!f) return;
      const href = catalog.previewHref(f, sample);
      if (loaded.has(href)) return;
      loaded.add(href);
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = href;
      document.head.appendChild(link);
    });
    io.observe(node);
    return { destroy: () => io.disconnect() };
  }

  // Ouvert depuis l'Aperçu avancé : on n'y montre que les polices variables et on y revient après le téléchargement.
  const forPreview = ui.returnTo === 'variables';
  if (forPreview) catalog.variableOnly = true;

  async function download() {
    const added = await catalog.downloadSelected();
    if (!added.length) return;
    session.toast = { kind: 'added', count: added.length };
    if (forPreview) {
      session.selectedId = added[0];
      ui.go('variables');
    } else {
      ui.go('conversion');
    }
  }

  const selNames = $derived(catalog.selected);
</script>

<div class="flex min-h-full flex-col gap-[18px] px-[26px] pt-6 pb-[22px]">
  <div class="flex flex-col gap-2">
    <h1 class="m-0 font-display text-[31px] leading-[1.15] font-semibold tracking-[-0.01em] text-fg">{t('gf.title')}</h1>
    <p class="m-0 text-[14.5px] leading-normal text-fg-muted">{t('gf.subtitle')}</p>
  </div>

  <div class="flex flex-wrap items-center gap-3">
    <label class="flex min-h-11 flex-[1_1_300px] items-center gap-2.5 rounded-[10px] border border-line-strong bg-elevated px-3.5 text-fg-muted focus-within:border-focus">
      <Icon name="search" size={19} />
      <span class="sr-only">{t('gf.searchLabel')}</span>
      <input
        type="search"
        bind:value={catalog.query}
        placeholder={t('gf.search')}
        class="min-w-0 flex-1 bg-transparent text-[16px] text-fg outline-none placeholder:text-fg-subtle"
      />
    </label>
    <div class="flex min-h-11 items-center gap-1 rounded-[10px] border border-line-strong pl-3.5">
      <span id="var-{id}" class="text-[14.5px] whitespace-nowrap text-fg">{t('gf.variableOnly')}</span>
      <Toggle checked={catalog.variableOnly} labelledby="var-{id}" onchange={(v) => (catalog.variableOnly = v)} />
    </div>
  </div>

  <div role="group" aria-label={t('gf.category')} class="flex flex-wrap items-center gap-2">
    {#each cats as k (k)}
      <button
        type="button"
        aria-pressed={catalog.category === k}
        onclick={() => (catalog.category = k)}
        class="min-h-10 rounded-full px-4 text-[14px] whitespace-nowrap {catalog.category === k ? 'bg-gold-flat font-semibold' : 'border border-line-strong font-medium text-fg-muted hover:text-fg'}"
      >
        {t('gf.cats.' + k)}
      </button>
    {/each}
    {#if catalog.state === 'ready'}
      <span class="ml-auto text-[13px] text-fg-subtle">{t('gf.count', { count: catalog.filtered.length })}</span>
    {/if}
  </div>

  {#if catalog.state === 'loading' || catalog.state === 'idle'}
    <p role="status" class="flex min-h-[300px] items-center justify-center gap-3 text-fg-muted">
      <span aria-hidden="true" class="size-4 animate-spin rounded-full border-2 border-line-strong border-t-accent"></span>
      {t('gf.loading')}
    </p>
  {:else if catalog.state === 'error' || catalog.state === 'unavailable'}
    <div class="flex min-h-[300px] flex-col items-center justify-center gap-3 rounded-xl border-[1.5px] border-dashed border-accent-dash bg-sunken p-8 text-center">
      <Icon name="alert" size={36} stroke={1.3} class="text-accent-text" />
      <p class="m-0 text-fg-muted">{catalog.state === 'error' ? t('gf.loadError') : t('gf.desktopOnly')}</p>
      {#if catalog.state === 'error'}
        <button type="button" onclick={() => catalog.load(true)} class="inline-flex min-h-11 items-center gap-2 rounded-[9px] border border-line-strong px-4 text-[14.5px] text-fg hover:bg-hover">
          <Icon name="replay" size={18} />{t('gf.retry')}
        </button>
      {/if}
    </div>
  {:else if shown.length === 0}
    <div class="flex min-h-[300px] flex-col items-center justify-center gap-3 rounded-xl border-[1.5px] border-dashed border-accent-dash bg-sunken p-8 text-center">
      <Icon name="search" size={40} stroke={1.2} class="text-accent-text" />
      <p class="m-0 font-display text-[22px] font-semibold text-fg">{t('gf.emptyTitle')}</p>
      <p class="m-0 text-fg-muted">{t('gf.emptyBody')}</p>
      <button type="button" onclick={() => catalog.resetFilters()} class="inline-flex min-h-11 items-center gap-2 rounded-[9px] border border-line-strong px-4 text-[14.5px] text-fg hover:bg-hover">
        <Icon name="replay" size={18} />{t('gf.reset')}
      </button>
    </div>
  {:else}
    <div class="grid grid-cols-[repeat(auto-fill,minmax(min(270px,100%),1fr))] gap-3.5">
      {#each shown as f (f.family)}
        {@const on = catalog.selected.includes(f.family)}
        <article use:preview={f.family} class="flex flex-col gap-3.5 rounded-xl border px-[18px] pt-[18px] pb-4 shadow-card {on ? 'border-accent-line bg-selected-soft' : 'bg-card border-line'}">
          <div class="flex items-start justify-between gap-3">
            <div class="flex min-w-0 flex-col gap-[3px]">
              <h2 class="m-0 text-[15px] font-semibold text-fg">{f.family}</h2>
              <span class="text-[12.5px] text-fg-muted">{[t('gf.cats.' + f.category), t('gf.styles', { count: f.styles })].join(' · ')}</span>
            </div>
            <button
              type="button"
              aria-pressed={on}
              aria-label={t(on ? 'gf.removeFamily' : 'gf.add', { name: f.family })}
              title={t(on ? 'gf.removeFamily' : 'gf.add', { name: f.family })}
              onclick={() => catalog.toggle(f.family)}
              class="-mt-1 inline-flex min-h-9 shrink-0 items-center gap-1.5 rounded-[9px] px-3 text-[13px] font-semibold whitespace-nowrap {on
                ? 'border-[1.5px] border-accent bg-selected text-fg'
                : 'border border-line-strong text-fg-muted hover:bg-hover hover:text-fg'}"
            >
              <Icon name={on ? 'check' : 'plus'} size={15} />
              {t(on ? 'gf.added' : 'gf.addShort')}
            </button>
          </div>
          <p class="m-0 h-[68px] overflow-hidden text-[28px] leading-[1.2] text-specimen" style:font-family="'{f.family}', var(--font-sans)" style:font-weight={f.previewWeight}>
            {sample}
          </p>
          <div class="flex flex-wrap gap-x-3.5 gap-y-1 border-t border-line pt-2.5">
            {#if f.axes.length}
              {#each f.axes as a (a.tag)}
                <span class="text-[12.5px] whitespace-nowrap text-fg-muted">{a.tag} {fmt.num(a.min)}–{fmt.num(a.max)}</span>
              {/each}
            {:else}
              <span class="text-[12.5px] text-fg-muted">{t('conv.static')}</span>
            {/if}
          </div>
        </article>
      {/each}
    </div>
    {#if catalog.filtered.length > shown.length}
      <button type="button" onclick={() => (catalog.limit += 60)} class="mx-auto inline-flex min-h-11 items-center gap-2 rounded-[9px] border border-line-strong px-5 text-[14.5px] text-fg hover:bg-hover">
        {t('gf.more')}
      </button>
    {/if}
  {/if}

  <div class="sticky bottom-3.5 mt-auto flex flex-wrap items-center justify-between gap-3 rounded-xl border border-line-strong bg-elevated py-2.5 pr-2.5 pl-[18px] shadow-pop">
    <div class="flex min-w-0 items-center gap-3.5">
      <span aria-hidden="true" class="shrink-0 font-display text-[34px] leading-none font-semibold text-accent-text">{fmt.num(selNames.length)}</span>
      <div class="flex min-w-0 flex-col gap-[3px]">
        <span class="text-[14.5px] font-semibold text-fg">
          {#if catalog.download}
            {t('gf.downloading', { done: fmt.num(catalog.download.done), total: fmt.num(catalog.download.total) })}
          {:else}
            {selNames.length ? t('gf.selCount', { count: selNames.length }) : t('gf.selNone')}
          {/if}
        </span>
        <span class="text-[13px] text-fg-muted">
          {#if catalog.download?.failed.length}
            <span class="text-error">{t('gf.downloadError', { name: fmt.list(catalog.download.failed) })}</span>
          {:else}
            {selNames.length ? t('gf.selNames', { list: fmt.list(selNames) }) : t('gf.selHint')}
          {/if}
        </span>
      </div>
    </div>
    {#if selNames.length}
      <button type="button" onclick={download} disabled={!!catalog.download && catalog.download.done < catalog.download.total} class="bg-gold inline-flex min-h-[46px] items-center gap-2.5 rounded-[10px] px-5 text-[15px] font-semibold disabled:opacity-70">
        <Icon name="cloudDown" size={20} stroke={1.6} />
        <span class="whitespace-nowrap">{t(forPreview ? 'gf.ctaPreview' : 'gf.cta')}</span>
      </button>
    {:else}
      <span class="inline-flex min-h-[46px] items-center rounded-[10px] bg-surface px-[18px] text-[14.5px] whitespace-nowrap text-disabled">{t('gf.nothing')}</span>
    {/if}
  </div>
</div>
