<script lang="ts">
  import Icon from '../components/Icon.svelte';
  import Select from '../components/Select.svelte';
  import { t, fmt } from '../lib/i18n/index.svelte';
  import { session, type ExportSpec, type FontItem } from '../lib/state/session.svelte';
  import { ui } from '../lib/state/ui.svelte';
  import type { Axis } from '../lib/engine/types';

  const id = $props.id();
  const fonts = $derived(session.items.filter((i) => i.status === 'ready' && i.info?.variable));
  let chosenId = $state<string | null>(null);
  const font = $derived<FontItem | undefined>(fonts.find((f) => f.id === chosenId) ?? (session.selected?.info?.variable ? session.selected : fonts[0]));
  const info = $derived(font?.info);
  const axes = $derived((info?.axes ?? []).filter((a) => !a.hidden));

  let positions = $state<Record<string, Record<string, number>>>({});
  const pos = $derived.by(() => {
    if (!font || !info) return {} as Record<string, number>;
    const base = Object.fromEntries(info.axes.map((a) => [a.tag, a.default]));
    return { ...base, ...(positions[font.id] ?? {}) };
  });
  const setAxis = (tag: string, v: number) => {
    if (!font) return;
    positions[font.id] = { ...(positions[font.id] ?? {}), [tag]: v };
  };

  let sample = $state('');
  const text = $derived(sample || t('vf.sample'));
  let size = $state(56);
  let copied = $state(false);
  let exportKind = $state<'var' | 'pos' | 'all'>('var');

  const label = (a: Axis) => (a.tag === 'wght' ? t('vf.weight') : a.tag === 'wdth' ? t('vf.width') : a.tag === 'opsz' ? t('vf.opsz') : a.name || t('vf.axisGeneric', { tag: a.tag }));
  const valueText = (a: Axis, v: number) => (a.tag === 'wdth' ? fmt.num(v, 1) + ' %' : fmt.num(v, a.max - a.min <= 2 ? 2 : 0));

  const fvs = $derived(Object.entries(pos).map(([k, v]) => `'${k}' ${Math.round(v * 100) / 100}`).join(', '));
  const cssLine = $derived.by(() => {
    const parts: string[] = [];
    const rest: string[] = [];
    for (const [k, raw] of Object.entries(pos)) {
      const v = Math.round(raw * 100) / 100;
      if (k === 'wght') parts.push(`font-weight: ${v};`);
      else if (k === 'wdth') parts.push(`font-stretch: ${v}%;`);
      else if (k === 'slnt') parts.push(`font-style: oblique ${-v}deg;`);
      else rest.push(`'${k}' ${v}`);
    }
    if (rest.length) parts.push(`font-variation-settings: ${rest.join(', ')};`);
    return parts.join(' ');
  });

  const instanceOn = (coords: Record<string, number>) => Object.entries(coords).every(([k, v]) => Math.abs((pos[k] ?? 0) - v) < 0.01);
  const matching = $derived(info?.instances.find((i) => instanceOn(i.coords)));

  const tables = $derived((info?.tables ?? []).filter((x) => ['fvar', 'gvar', 'avar', 'HVAR', 'VVAR', 'MVAR', 'STAT', 'CFF2', 'cvar'].includes(x)));
  const stats = $derived(
    info && font
      ? [
          [t('vf.glyphs'), fmt.num(info.glyphs)],
          [t('vf.instancesCount'), fmt.num(info.instances.length)],
          [t('vf.fileSize'), fmt.size(font.size)],
          [t('vf.outlines'), info.outlines],
        ]
      : [],
  );

  const posSub = $derived(
    [...axes.map((a) => `${label(a)} ${valueText(a, pos[a.tag])}`), t('vf.exportAllSub', { count: 1 })].join(' · '),
  );
  const exportsList = $derived([
    { id: 'var' as const, title: t('vf.exportVar'), sub: t('vf.exportVarSub') },
    { id: 'pos' as const, title: t('vf.exportPos'), sub: posSub },
    { id: 'all' as const, title: t('vf.exportAll', { count: info?.instances.length ?? 0 }), sub: t('vf.exportAllSub', { count: info?.instances.length ?? 0 }) },
  ]);

  function addToConversion() {
    if (!font || !info) return;
    let spec: ExportSpec = { kind: 'keep' };
    if (exportKind === 'all') spec = { kind: 'all' };
    if (exportKind === 'pos') {
      const name = matching?.name || axes.map((a) => `${a.tag}${Math.round(pos[a.tag])}`).join(' ');
      spec = { kind: 'instance', instance: { name, coords: { ...pos } } };
    }
    session.addDerived(font.id, spec);
    session.toast = { kind: 'added', count: 1 };
    ui.go('conversion');
  }

  async function copy() {
    try {
      await navigator.clipboard.writeText(cssLine);
      copied = true;
      setTimeout(() => (copied = false), 1600);
    } catch {
      copied = false;
    }
  }

  const sizes = [
    ['s', 40],
    ['m', 56],
    ['l', 72],
    ['xl', 96],
  ] as const;
</script>

<div class="flex flex-col gap-[18px] px-[26px] pt-6 pb-[22px]">
  <div class="flex flex-wrap items-end justify-between gap-3.5">
    <div class="flex min-w-0 flex-col gap-2">
      <h1 class="m-0 font-display text-[31px] leading-[1.15] font-semibold tracking-[-0.01em] text-fg">{t('vf.title')}</h1>
      <p class="m-0 text-[14.5px] leading-normal text-fg-muted">{t('vf.subtitle')}</p>
    </div>
    {#if font}
      <div class="min-w-[220px] flex-[0_1_300px]">
        <span id="font-{id}" class="sr-only">{t('vf.font')}</span>
        <Select
          value={font.id}
          labelledby="font-{id}"
          menuWidth="w-full"
          triggerClass="min-h-[52px] rounded-[10px] py-1.5 pl-2"
          options={fonts.map((f) => ({ id: f.id, label: f.info?.family ?? f.fileName, hint: `${f.fileName} · ${t('conv.axes', { count: f.info?.axes.length ?? 0 })}` }))}
          onchange={(v) => (chosenId = v)}
        >
          {#snippet lead()}
            <span class="flex size-[34px] shrink-0 items-center justify-center rounded-[7px] bg-sunken text-[17px] text-fg" style:font-family={font?.previewFamily ?? 'inherit'}>Aa</span>
          {/snippet}
        </Select>
      </div>
    {/if}
  </div>

  {#if !font || !info}
    <div class="flex min-h-[360px] flex-col items-center justify-center gap-3 rounded-xl border-[1.5px] border-dashed border-accent-dash bg-sunken p-8 text-center">
      <Icon name="variables" size={40} stroke={1.2} class="text-accent-text" />
      <p class="m-0 font-display text-[22px] font-semibold text-fg">{t('vf.emptyTitle')}</p>
      <p class="m-0 max-w-md text-fg-muted">{t('vf.emptyBody')}</p>
      <div class="flex flex-wrap justify-center gap-2.5">
        <button type="button" onclick={() => ui.go('conversion')} class="bg-gold inline-flex min-h-11 items-center gap-2 rounded-[9px] px-4 text-[14.5px] font-semibold">
          <Icon name="convert" size={18} />{t('vf.goConvert')}
        </button>
        <button type="button" onclick={() => ui.go('google')} class="inline-flex min-h-11 items-center gap-2 rounded-[9px] border border-line-strong px-4 text-[14.5px] text-fg hover:bg-hover">
          <Icon name="google" size={18} />{t('nav.google')}
        </button>
      </div>
    </div>
  {:else}
    <div class="flex flex-wrap items-start gap-5">
      <section aria-label={t('conv.previewTabs')} class="flex min-w-0 flex-[999_1_440px] flex-col gap-4 rounded-xl border border-line bg-sunken px-5 py-[18px]">
        <div class="flex flex-wrap items-end gap-2.5">
          <label class="flex flex-[1_1_260px] flex-col gap-[7px]">
            <span class="text-[13px] text-fg-muted">{t('vf.sampleLabel')}</span>
            <input type="text" bind:value={sample} placeholder={t('vf.sample')} class="min-h-[42px] rounded-lg border border-line-strong bg-elevated px-3 text-[16px] text-fg placeholder:text-fg-subtle" />
          </label>
          <div class="flex flex-[0_1_170px] flex-col gap-[7px]">
            <span id="size-{id}" class="text-[13px] text-fg-muted">{t('vf.size')}</span>
            <div role="group" aria-labelledby="size-{id}" class="grid grid-cols-4 gap-0.5 rounded-[9px] border border-line-strong bg-elevated p-[3px]">
              {#each sizes as [k, v] (k)}
                <button
                  type="button"
                  aria-pressed={size === v}
                  title="{t('vf.sizeHint.' + k)} · {t('vf.px', { value: fmt.num(v) })}"
                  onclick={() => (size = v)}
                  class="min-h-9 rounded-md text-[13px] {size === v ? 'bg-gold-flat font-semibold' : 'text-fg-muted hover:text-fg'}"
                >
                  {fmt.num(v)}
                </button>
              {/each}
            </div>
          </div>
        </div>

        <div class="flex h-44 items-center overflow-hidden rounded-[10px] border border-line bg-surface px-2">
          <p data-selectable class="m-0 px-3 leading-[1.12] [overflow-wrap:anywhere] text-specimen" style:font-family={font.previewFamily ?? 'inherit'} style:font-size="{size}px" style:font-variation-settings={fvs}>
            {text}
          </p>
        </div>

        <div class="flex flex-col gap-1">
          {#each axes as a (a.tag)}
            <div class="flex items-center gap-3.5">
              <label for="ax-{id}-{a.tag}" class="flex w-[130px] shrink-0 flex-col gap-0.5">
                <span class="text-[14.5px] font-semibold text-fg">{label(a)}</span>
                <span class="text-[12.5px] text-accent-text">{a.tag} · {fmt.num(a.min)}–{fmt.num(a.max)}</span>
              </label>
              <input
                id="ax-{id}-{a.tag}"
                type="range"
                min={a.min}
                max={a.max}
                step={a.max - a.min <= 2 ? 0.01 : a.tag === 'wdth' ? 0.5 : 1}
                value={pos[a.tag]}
                oninput={(e) => setAxis(a.tag, parseFloat((e.currentTarget as HTMLInputElement).value))}
                class="h-11 min-w-0 flex-1 cursor-pointer accent-[var(--ftn-accent)]"
              />
              <span class="min-w-14 shrink-0 text-right text-[15px] font-semibold whitespace-nowrap text-fg">{valueText(a, pos[a.tag])}</span>
            </div>
          {/each}
        </div>

        {#if info.instances.length}
          <div class="flex flex-col gap-[9px]">
            <span class="text-[13px] text-fg-muted">{t('vf.instances')}</span>
            <div class="flex flex-wrap gap-1.5">
              {#each info.instances as inst, i (i)}
                {@const on = instanceOn(inst.coords)}
                <button
                  type="button"
                  aria-pressed={on}
                  onclick={() => font && (positions[font.id] = { ...inst.coords })}
                  class="min-h-[38px] rounded-lg px-3 text-[13.5px] whitespace-nowrap {on ? 'border border-accent-line bg-selected font-semibold text-fg' : 'border border-line-strong text-fg-muted hover:text-fg'}"
                >
                  {inst.name || '—'}
                </button>
              {/each}
            </div>
          </div>
        {/if}

        <div class="flex items-center justify-between gap-2.5 rounded-[9px] border border-line bg-surface py-1.5 pr-1.5 pl-3.5">
          <code class="min-w-0 font-mono text-[13px] [overflow-wrap:anywhere] text-code-text">{cssLine}</code>
          <button type="button" onclick={copy} class="inline-flex min-h-[38px] shrink-0 items-center gap-[7px] rounded-lg border border-line-strong px-3 text-[13.5px] whitespace-nowrap text-fg hover:bg-hover">
            <Icon name={copied ? 'checkCircle' : 'copy'} size={16} />
            {copied ? t('vf.copied') : t('vf.copy')}
          </button>
        </div>
      </section>

      <div class="flex min-w-0 flex-[1_1_300px] flex-col gap-4">
        <section aria-labelledby="det-{id}" class="bg-card shadow-card flex flex-col gap-3.5 rounded-xl border border-line px-5 py-[18px]">
          <div class="flex items-center gap-2.5">
            <Icon name="info" size={19} class="text-fg" />
            <h2 id="det-{id}" class="m-0 text-[15px] font-semibold text-fg">{t('vf.details')}</h2>
          </div>
          <dl class="m-0 grid grid-cols-2 gap-2.5">
            {#each stats as [l, v] (l)}
              <div class="flex flex-col gap-1 rounded-[9px] border border-line bg-sunken px-3 py-2.5">
                <dt class="text-[12.5px] text-fg-subtle">{l}</dt>
                <dd class="m-0 font-display text-[20px] font-semibold text-fg">{v}</dd>
              </div>
            {/each}
          </dl>
          {#if tables.length}
            <span class="text-[13px] leading-normal text-fg-muted">{t('vf.tables', { list: fmt.list(tables) })}</span>
          {/if}
        </section>

        <section aria-labelledby="exp-{id}" class="bg-card shadow-card flex flex-col gap-2.5 rounded-xl border border-line px-5 py-[18px]">
          <div class="mb-0.5 flex items-center gap-2.5">
            <Icon name="layers" size={19} class="text-fg" />
            <h2 id="exp-{id}" class="m-0 text-[15px] font-semibold text-fg">{t('vf.exportTitle')}</h2>
          </div>
          <div role="radiogroup" aria-labelledby="exp-{id}" class="flex flex-col gap-2">
            {#each exportsList as e (e.id)}
              {@const on = exportKind === e.id}
              <button
                type="button"
                role="radio"
                aria-checked={on}
                disabled={e.id === 'all' && !info.instances.length}
                onclick={() => (exportKind = e.id)}
                class="flex min-h-[58px] items-center gap-3 rounded-[10px] border px-3 py-2.5 text-left disabled:opacity-50 {on ? 'border-accent-line bg-selected-soft' : 'border-line hover:bg-hover'}"
              >
                <span aria-hidden="true" class="size-[18px] shrink-0 rounded-full {on ? 'bg-gold-flat shadow-[inset_0_0_0_5px_var(--ftn-surface),0_0_0_1px_var(--ftn-accent)]' : 'border-[1.5px] border-line-strong'}"></span>
                <span class="flex min-w-0 flex-col gap-[3px]">
                  <span class="text-[14.5px] font-semibold text-fg">{e.title}</span>
                  <span class="text-[12.5px] text-fg-muted">{e.sub}</span>
                </span>
              </button>
            {/each}
          </div>
          <button type="button" onclick={addToConversion} class="bg-gold mt-1 flex min-h-[50px] items-center justify-center gap-2.5 rounded-[10px] text-[16px] font-semibold">
            <Icon name="plus" size={19} stroke={1.7} />
            <span class="whitespace-nowrap">{t('vf.cta')}</span>
          </button>
        </section>
      </div>
    </div>
  {/if}
</div>
