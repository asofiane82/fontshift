<script lang="ts">
  import Icon from '../components/Icon.svelte';
  import Select from '../components/Select.svelte';
  import Toggle from '../components/Toggle.svelte';
  import InfoTip from '../components/InfoTip.svelte';
  import Toast from '../components/Toast.svelte';
  import Specimen from '../components/Specimen.svelte';
  import { t, fmt } from '../lib/i18n/index.svelte';
  import { session, styleKey, styleName, type FontItem, type Subset } from '../lib/state/session.svelte';
  import { ui } from '../lib/state/ui.svelte';
  import { engine } from '../lib/engine/client.svelte';
  import type { Format } from '../lib/engine/types';
  import { filesFromBrowser, isTauri, pickFolder, pickFontPaths, FONT_EXTENSIONS } from '../lib/platform';

  const id = $props.id();
  let fileInput: HTMLInputElement | undefined = $state();
  let htmlDrag = $state(false);
  let tab = $state<'preview' | 'details' | 'glyphs'>('preview');
  let expanded = $state(false);

  // Destination : affiche le sous-dossier réel de la prochaine conversion (polices, dossier, fin de conversion).
  $effect(() => {
    void session.folderLabel;
    void session.dest;
    void session.phase;
    void session.results;
    void session.refreshNextFolder();
  });

  const sel = $derived(session.selected);
  const dragging = $derived(ui.dragging || htmlDrag);
  const count = $derived(session.ready.length);
  const formats: { id: Format; label: string }[] = [
    { id: 'woff2', label: 'WOFF2' },
    { id: 'woff', label: 'WOFF' },
    { id: 'ttf', label: 'TTF' },
    { id: 'otf', label: 'OTF' },
    { id: 'eot', label: 'EOT' },
  ];

  async function browse() {
    if (isTauri) {
      const paths = await pickFontPaths(t('conv.browse'));
      if (paths?.length) await session.addPaths(paths);
    } else fileInput?.click();
  }

  async function onHtmlDrop(e: DragEvent) {
    e.preventDefault();
    htmlDrag = false;
    if (!isTauri && e.dataTransfer?.files.length) await session.addFiles(await filesFromBrowser(e.dataTransfer.files));
  }

  async function chooseDest() {
    const dir = await pickFolder(t('conv.destChoose'), session.dest);
    if (dir) {
      session.dest = dir;
      session.saveOptions();
    }
  }

  function meta(item: FontItem) {
    const info = item.info!;
    const parts = [info.variable ? t('conv.variable') : t('conv.static')];
    if (info.variable) parts.push(t('conv.axes', { count: info.axes.length }));
    parts.push(fmt.size(item.size));
    const spec = item.exportSpec;
    if (spec.kind === 'instance') parts.push(spec.instance.name || t('conv.static'));
    if (spec.kind === 'all') parts.push(t('vf.exportAllSub', { count: info.instances.length }));
    return parts.join(' · ');
  }

  const subsetOptions = $derived(
    (['full', 'latin', 'latinExt', 'custom'] as Subset[]).map((k) => ({ id: k, label: t('conv.subset.' + k), hint: t('conv.subsetHint.' + k) })),
  );

  const details = $derived.by(() => {
    const info = sel?.info;
    if (!sel || !info) return [];
    return [
      [t('conv.details.family'), info.family || '—'],
      [t('conv.details.style'), info.style || '—'],
      [t('conv.details.format'), `${info.sourceFormat} · ${info.outlines}`],
      [t('conv.details.glyphs'), fmt.num(info.glyphs)],
      [t('conv.details.axes'), info.variable ? info.axes.map((a) => a.tag).join(', ') : t('conv.static')],
      [t('conv.details.instances'), info.instances.length ? fmt.num(info.instances.length) : '—'],
      [t('conv.details.size'), fmt.size(sel.size)],
      [t('conv.details.version'), info.version.replace(/^Version\s*/i, '') || '—'],
    ];
  });

  const toast = $derived.by(() => {
    const tt = session.toast;
    if (!tt) return null;
    const r = session.results;
    if (tt.kind === 'done' && r) {
      const from = r.sources.reduce((a, s) => a + s.size, 0);
      const primary = r.sources.map((s) => r.outputs.filter((o) => o.sourceId === s.id).sort((a, b) => a.size - b.size)[0]).filter(Boolean);
      const to = primary.reduce((a, o) => a + o.size, 0);
      return { title: t('toast.doneTitle', { count: tt.count }), body: t('toast.doneBody', { pct: fmt.pct(to / from - 1), size: fmt.size(to) }), tone: 'success' as const };
    }
    if (tt.kind === 'error') return { title: t('toast.errorTitle'), body: t('conv.failedCount', { count: tt.failed ?? 0 }), tone: 'warning' as const };
    if (tt.kind === 'added') return { title: t('toast.addedTitle', { count: tt.count }), body: t('toast.addedBody'), tone: 'success' as const };
    return { title: t('conv.cancelled'), body: '', tone: 'neutral' as const };
  });

  const tabs = $derived([
    ['preview', t('conv.tabPreview')],
    ['details', t('conv.tabDetails')],
    ['glyphs', t('conv.tabGlyphs')],
  ] as const);
</script>

<div class="flex flex-wrap items-start gap-5 px-[26px] pt-6 pb-6">
  <!-- Colonne gauche : dépôt et file -->
  <section class="flex min-w-0 flex-[1_1_380px] flex-col gap-[18px]">
    <div class="flex flex-col gap-2">
      <h1 class="m-0 font-display text-[31px] leading-[1.15] font-semibold tracking-[-0.01em] text-fg">{t('conv.title')}</h1>
      <p class="m-0 text-[14.5px] leading-normal text-fg-muted">{t('conv.subtitle')}</p>
    </div>

    <section
      aria-label={t('conv.dropAria')}
      ondragover={(e) => {
        e.preventDefault();
        htmlDrag = true;
      }}
      ondragleave={() => (htmlDrag = false)}
      ondrop={onHtmlDrop}
      class="flex flex-col items-center justify-center gap-[9px] rounded-xl border-[1.5px] border-dashed px-5 pt-[26px] pb-6 transition-colors {dragging ? 'border-accent bg-selected-soft' : 'border-accent-dash bg-sunken'}"
    >
      <Icon name="cloudUp" size={46} stroke={1.2} class="text-accent-text" />
      <span class="text-center text-[17px] font-semibold text-fg">{dragging ? t('conv.dropRelease', { count: ui.dragCount }) : t('conv.dropTitle')}</span>
      <span class="text-center text-[13px] text-fg-muted">{t('conv.dropFormats')}</span>
      <button type="button" onclick={browse} class="bg-gold mt-1.5 inline-flex min-h-[42px] items-center gap-[9px] rounded-[9px] px-5 text-[14.5px] font-semibold">
        <Icon name="folder" size={18} stroke={1.6} />
        <span class="whitespace-nowrap">{t('conv.browse')}</span>
      </button>
      <input
        bind:this={fileInput}
        type="file"
        multiple
        accept={FONT_EXTENSIONS.map((e) => '.' + e).join(',')}
        class="sr-only"
        tabindex="-1"
        aria-hidden="true"
        onchange={async (e) => {
          const input = e.currentTarget as HTMLInputElement;
          if (input.files?.length) await session.addFiles(await filesFromBrowser(input.files));
          input.value = '';
        }}
      />
    </section>

    {#if session.items.length}
      <div class="bg-card shadow-card overflow-hidden rounded-xl border border-line">
        <div class="flex flex-wrap items-center justify-between gap-x-3 gap-y-1.5 border-b border-line py-2 pr-2 pl-4">
          <span class="text-[13.5px] text-fg-muted">{t('conv.listSummary', { count, size: fmt.size(session.totalSize) })}</span>
          {#if session.phase !== 'done'}
            <button type="button" onclick={() => session.clear()} class="inline-flex min-h-9 items-center gap-[7px] rounded-lg px-2.5 text-[13.5px] whitespace-nowrap text-fg-muted hover:bg-hover hover:text-fg">
              <Icon name="trash" size={16} />
              {t('conv.clearAll')}
            </button>
          {/if}
        </div>
        <ul class="m-0 list-none p-0">
          {#each session.items as item (item.id)}
            {@const isSel = sel?.id === item.id}
            {@const run = item.run}
            <li class="flex items-center gap-2.5 border-t border-line py-2.5 pr-2 pl-4 first:border-t-0 {isSel ? 'bg-selected-soft' : ''}">
              <button type="button" aria-pressed={isSel} onclick={() => (session.selectedId = item.id)} class="flex min-w-0 flex-1 items-center gap-3.5 text-left">
                <span
                  aria-hidden="true"
                  class="flex size-[42px] shrink-0 items-center justify-center rounded-lg border bg-elevated text-[19px] text-fg {item.status === 'error' || run?.state === 'failed' ? 'border-error-line' : 'border-line'}"
                  style:font-family={item.previewFamily ?? 'inherit'}>Aa</span
                >
                <span class="flex min-w-0 flex-col gap-[3px]">
                  <span class="text-[14.5px] font-semibold [overflow-wrap:anywhere] text-fg">{item.fileName}</span>
                  {#if item.status === 'analysing'}
                    <span class="text-[12.5px] text-fg-subtle">{t('conv.analysing')}</span>
                  {:else if item.status === 'error' || run?.state === 'failed'}
                    <span class="inline-flex items-center gap-1.5 text-[12.5px] text-error">
                      <Icon name="alert" size={15} stroke={1.6} />
                      {t(item.error ?? run?.error ?? 'conv.errorConvert')}
                    </span>
                  {:else}
                    <span class="text-[12.5px] text-fg-muted">{meta(item)}</span>
                  {/if}
                </span>
              </button>
              {#if run?.state === 'waiting'}
                <span class="shrink-0 text-[12.5px] whitespace-nowrap text-fg-subtle">{t('conv.waiting')}</span>
              {:else if run?.state === 'running'}
                <span class="flex shrink-0 flex-col items-end gap-1.5">
                  <span class="text-[12.5px] whitespace-nowrap text-fg-muted">{t('conv.converting', { pct: fmt.pct(run.progress).replace('+', '') })}</span>
                  <span class="h-[3px] w-24 overflow-hidden rounded-[3px] bg-line"><span class="bg-gold-flat block h-full transition-[width] duration-100" style:width="{run.progress * 100}%"></span></span>
                </span>
              {:else if run?.state === 'done'}
                <span title={t('conv.converted')} class="inline-flex shrink-0 items-center gap-[5px] rounded-md bg-success-soft px-2 py-[3px] text-[12.5px] font-semibold whitespace-nowrap text-success">
                  <Icon name="check" size={14} />
                  {fmt.pct(run.gain ?? 0)}
                </span>
              {/if}
              <button
                type="button"
                onclick={() => session.remove(item.id)}
                disabled={session.phase === 'running'}
                aria-label={t('conv.remove', { name: item.fileName })}
                title={t('conv.remove', { name: item.fileName })}
                class="flex size-9 shrink-0 items-center justify-center rounded-lg text-fg-muted hover:bg-hover hover:text-fg disabled:opacity-40"
              >
                <Icon name="close" size={17} stroke={1.6} />
              </button>
            </li>
          {/each}
        </ul>
      </div>
    {/if}
    {#if engine.state === 'loading' && session.items.some((i) => i.status === 'analysing')}
      <p class="m-0 flex items-center gap-2 text-[13px] text-fg-muted" role="status">
        <span class="size-3.5 animate-spin rounded-full border-2 border-line-strong border-t-accent" aria-hidden="true"></span>
        {t('conv.engineLoading')}
      </p>
    {:else if engine.state === 'error'}
      <p class="m-0 flex items-center gap-2 text-[13px] text-error" role="alert" title={engine.detail}><Icon name="alert" size={16} />{t('conv.errorEngine')}</p>
    {/if}
  </section>

  <!-- Colonne droite : aperçu, formats, options, action -->
  <section class="flex min-w-0 flex-[1_1_420px] flex-col gap-4">
    <div class="overflow-hidden rounded-xl border border-line bg-sunken">
      <div class="flex items-center gap-1.5 border-b border-line pt-2.5 pr-2.5 pl-3">
        <div role="tablist" aria-label={t('conv.previewTabs')} class="flex min-w-0 flex-1 flex-wrap gap-1">
          {#each tabs as [k, label] (k)}
            <button
              type="button"
              role="tab"
              aria-selected={tab === k}
              onclick={() => (tab = k)}
              class="min-h-10 rounded-t-lg px-4 text-[14.5px] whitespace-nowrap {tab === k ? 'bg-selected-soft font-semibold text-fg shadow-[inset_0_-2px_0_var(--ftn-accent)]' : 'text-fg-muted hover:text-fg'}"
            >
              {label}
            </button>
          {/each}
        </div>
        <button
          type="button"
          onclick={() => (expanded = !expanded)}
          aria-pressed={expanded}
          aria-label={t('conv.expand')}
          title={t('conv.expand')}
          class="mb-1 flex size-10 shrink-0 items-center justify-center rounded-lg text-fg-muted hover:bg-hover hover:text-fg"
        >
          <Icon name="expand" size={19} />
        </button>
      </div>
      <div role="tabpanel" aria-label={tabs.find(([k]) => k === tab)?.[1]} class="flex items-center justify-center px-2.5 py-1.5 {expanded ? 'min-h-[440px]' : 'min-h-[250px]'}">
        {#if tab === 'preview'}
          <Specimen item={sel} />
        {:else if tab === 'details'}
          {#if sel?.info}
            <div class="flex w-full items-center gap-[22px] px-2 py-2.5">
              <span aria-hidden="true" class="shrink-0 text-[84px] leading-none text-specimen" style:font-family={sel.previewFamily ?? 'inherit'}>Ag</span>
              <dl class="m-0 grid min-w-0 flex-1 grid-cols-2 gap-x-[18px] gap-y-3">
                {#each details as [label, value] (label)}
                  <div class="flex flex-col gap-[3px] border-b border-line pb-2">
                    <dt class="text-[12.5px] text-fg-subtle">{label}</dt>
                    <dd class="m-0 text-[14.5px] font-medium [overflow-wrap:anywhere] text-fg">{value}</dd>
                  </div>
                {/each}
              </dl>
            </div>
          {:else}
            <p class="text-fg-muted">{t('conv.emptyList')}</p>
          {/if}
        {:else if sel?.info}
          <div class="flex w-full flex-col gap-2.5 px-1.5 py-2">
            <div aria-hidden="true" class="grid grid-cols-[repeat(auto-fill,minmax(34px,1fr))] gap-1">
              {#each sel.info.sample.slice(0, expanded ? 96 : 48) as ch, i (i)}
                <span class="flex h-[34px] items-center justify-center rounded-md bg-surface text-[19px] text-specimen" style:font-family={sel.previewFamily ?? 'inherit'}>{ch}</span>
              {/each}
            </div>
            <span class="text-[12.5px] text-fg-subtle">{t('conv.glyphsNote')}</span>
          </div>
        {:else}
          <p class="text-fg-muted">{t('conv.emptyList')}</p>
        {/if}
      </div>
    </div>

    <div class="bg-card shadow-card flex flex-col gap-3.5 rounded-xl border border-line px-5 py-[18px]">
      {#if session.variableItems.length}
        {@const choices = session.styleChoices}
        {@const withItalic = choices.some((c) => c.italic)}
        <div class="flex items-center gap-2.5">
          <Icon name="variables" size={19} class="text-fg" />
          <h2 id="sty-{id}" class="m-0 flex-1 text-[15px] font-semibold text-fg">{t('conv.stylesTitle')}</h2>
          <InfoTip topic={t('conv.stylesTitle')} text={t('conv.stylesInfo')} />
        </div>
        <div role="group" aria-labelledby="sty-{id}" class="grid gap-1.5 {withItalic ? 'grid-cols-2' : 'grid-cols-3'}">
          {#snippet chip(key: string, label: string, sub: string, wide = false)}
            {@const on = session.styles.includes(key)}
            <button
              type="button"
              aria-pressed={on}
              onclick={() => session.toggleStyle(key)}
              class="flex min-h-10 items-center gap-2 rounded-[9px] px-2.5 text-left {wide ? 'col-span-full' : ''} {on
                ? 'border-[1.5px] border-accent bg-selected text-fg'
                : 'border border-line bg-sunken text-fg-muted hover:border-line-strong hover:text-fg'}"
            >
              <span class="flex size-4 shrink-0 items-center justify-center">{#if on}<Icon name="check" size={15} />{/if}</span>
              <span class="min-w-0 flex-1 truncate text-[13.5px] font-semibold">{label}</span>
              <span class="shrink-0 text-[12px] whitespace-nowrap opacity-80">{sub}</span>
            </button>
          {/snippet}
          {@render chip('variable', t('conv.styleVariable'), t('conv.styleVariableSub'), true)}
          {#each choices as c (c.weight)}
            {#if c.upright}
              {@render chip(styleKey(c.weight, false), styleName(c.weight, false), String(c.weight))}
            {:else if withItalic}
              <span></span>
            {/if}
            {#if c.italic}
              {@render chip(styleKey(c.weight, true), styleName(c.weight, true), String(c.weight))}
            {:else if withItalic}
              <span></span>
            {/if}
          {/each}
        </div>
        <div class="h-px bg-line"></div>
      {/if}
      <div class="flex items-center gap-2.5">
        <Icon name="layers" size={19} class="text-fg" />
        <h2 class="m-0 text-[15px] font-semibold text-fg">{t('conv.formatsTitle')}</h2>
      </div>
      <div role="group" aria-label={t('conv.formatsTitle')} class="grid grid-cols-3 gap-2">
        {#each formats as f (f.id)}
          {@const on = session.formats[f.id]}
          <button
            type="button"
            aria-pressed={on}
            onclick={() => session.toggleFormat(f.id)}
            class="inline-flex min-h-11 items-center justify-center gap-1.5 rounded-[10px] px-2.5 text-[14px] font-semibold whitespace-nowrap {on
              ? 'border-[1.5px] border-accent bg-selected text-fg'
              : 'border border-line bg-sunken text-fg-muted hover:border-line-strong hover:text-fg'}"
          >
            {#if on}<Icon name="check" size={15} />{/if}
            {f.label}
          </button>
        {/each}
      </div>
      {#if session.formats.eot}
        <p class="m-0 flex items-center gap-2 rounded-lg bg-warning-soft px-2.5 py-2 text-[13px] text-warning">
          <Icon name="alert" size={16} stroke={1.6} />
          {t('conv.eotWarning')}
        </p>
      {/if}

      <div class="h-px bg-line"></div>

      <div class="flex items-center gap-2.5">
        <Icon name="variables" size={19} class="text-fg" />
        <h2 class="m-0 text-[15px] font-semibold text-fg">{t('conv.optionsTitle')}</h2>
      </div>
      <div class="flex flex-col gap-2">
        <div class="flex flex-wrap items-center gap-x-3 gap-y-1.5">
          <span id="sub-{id}" class="flex-[1_1_140px] text-[14.5px] text-fg-muted">{t('conv.optSubset')}</span>
          <div class="min-w-[180px] flex-[0_1_236px]">
            <Select
              value={session.subset}
              options={subsetOptions}
              labelledby="sub-{id}"
              onchange={(v) => {
                session.subset = v;
                session.saveOptions();
              }}
            />
          </div>
          <InfoTip topic={t('conv.optSubset')} text={t('conv.optSubsetInfo')} />
        </div>
        {#if session.subset === 'custom'}
          <label class="flex flex-col gap-1.5 pl-0.5">
            <span class="text-[13px] text-fg-muted">{t('conv.customLabel')}</span>
            <input
              type="text"
              bind:value={session.customText}
              onchange={() => session.saveOptions()}
              placeholder={t('conv.customPlaceholder')}
              class="min-h-10 rounded-lg border border-line-strong bg-elevated px-3 text-[15px] text-fg placeholder:text-fg-subtle"
            />
          </label>
        {/if}
        <div class="flex flex-wrap items-center gap-x-3 gap-y-1.5">
          <span id="css-{id}" class="flex-[1_1_140px] text-[14.5px] text-fg-muted">{t('conv.optCss')}</span>
          <Toggle
            checked={session.css}
            labelledby="css-{id}"
            onchange={(v) => {
              session.css = v;
              session.saveOptions();
            }}
          />
          <InfoTip topic={t('conv.optCss')} text={t('conv.optCssInfo')} />
        </div>
        <div class="flex flex-wrap items-center gap-x-3 gap-y-1.5">
          <span id="dest-{id}" class="flex-[1_1_140px] text-[14.5px] text-fg-muted">{t('conv.optDest')}</span>
          <button
            type="button"
            aria-labelledby="dest-{id} destv-{id}"
            onclick={chooseDest}
            title={session.nextFolder ? `${session.displayDest}/${session.nextFolder} — ${t('conv.destChoose')}` : t('conv.destChoose')}
            class="flex min-h-10 min-w-[180px] flex-[0_1_236px] items-center gap-2 rounded-lg border border-line-strong bg-elevated px-3 text-left text-[14px] text-fg hover:border-focus"
          >
            <Icon name="folder" size={17} class="text-fg-muted" />
            <span id="destv-{id}" class="flex min-w-0 flex-1">
              {#if session.nextFolder}
                <span class="min-w-0 shrink truncate text-fg-muted">{session.displayDest}/</span>
                <span class="min-w-0 shrink-[0.2] truncate font-semibold">{session.nextFolder}</span>
              {:else}
                <span class="min-w-0 truncate">{session.displayDest}</span>
              {/if}
            </span>
          </button>
          <InfoTip topic={t('conv.optDest')} text={t('conv.optDestInfo')} />
        </div>
      </div>

      {#if session.phase === 'running'}
        <div role="status" class="flex min-h-[50px] items-center gap-3.5">
          <div class="flex min-w-0 flex-1 flex-col gap-2">
            <span class="text-[14px] text-fg">{t('conv.running', { done: fmt.num(Math.min(session.progress.total, session.progress.done + 1)), total: fmt.num(session.progress.total) })}</span>
            <span class="h-1 overflow-hidden rounded bg-line">
              <span class="bg-gold-flat block h-full transition-[width] duration-200" style:width="{(session.progress.done / Math.max(1, session.progress.total)) * 100}%"></span>
            </span>
          </div>
          <button type="button" onclick={() => session.cancel()} class="min-h-10 shrink-0 rounded-[9px] border border-line-strong px-4 text-[14px] font-medium whitespace-nowrap text-fg hover:bg-hover">
            {t('conv.cancel')}
          </button>
        </div>
      {:else if session.phase === 'done'}
        <div class="flex flex-col gap-2">
          <button
            type="button"
            onclick={() => {
              session.unseen = false;
              ui.go('results');
            }}
            class="bg-gold flex min-h-[50px] items-center justify-center gap-2.5 rounded-[10px] px-[18px] text-[16px] font-semibold"
          >
            <span class="whitespace-nowrap">{t('conv.viewResults')}</span>
            <Icon name="arrowRight" size={19} stroke={1.7} />
          </button>
          <div class="grid grid-cols-2 gap-2">
            <button type="button" onclick={() => session.replay()} title={t('conv.replayHint')} class="inline-flex min-h-11 items-center justify-center gap-2 rounded-[10px] border border-line-strong px-3 text-[14px] font-medium whitespace-nowrap text-fg hover:bg-hover">
              <Icon name="replay" size={17} />
              {t('conv.replay')}
            </button>
            <button type="button" onclick={() => session.newSession()} title={t('conv.newHint')} class="inline-flex min-h-11 items-center justify-center gap-2 rounded-[10px] border border-line-strong px-3 text-[14px] font-medium whitespace-nowrap text-fg hover:bg-hover">
              <Icon name="plus" size={17} />
              {t('top.newSession')}
            </button>
          </div>
        </div>
      {:else}
        <button
          type="button"
          onclick={() => session.start()}
          disabled={count === 0 || engine.state === 'error'}
          class="flex min-h-[52px] items-center justify-center gap-3 rounded-[10px] px-5 text-[17px] font-semibold {count ? 'bg-gold' : 'bg-elevated text-disabled'}"
        >
          <Icon name="convert" size={21} stroke={1.7} />
          <span class="whitespace-nowrap">{t('conv.cta', { count })}</span>
        </button>
      {/if}
    </div>
  </section>
</div>

{#if toast}
  <Toast title={toast.title} body={toast.body} tone={toast.tone} onclose={() => (session.toast = null)} />
{/if}
