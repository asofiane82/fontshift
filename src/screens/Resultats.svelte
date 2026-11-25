<script lang="ts">
  import Icon from '../components/Icon.svelte';
  import { t, fmt } from '../lib/i18n/index.svelte';
  import { session } from '../lib/state/session.svelte';
  import { ui } from '../lib/state/ui.svelte';
  import { faceRules, highlight, tailwindSnippet } from '../lib/css';
  import { reveal } from '../lib/platform';

  const id = $props.id();
  const r = $derived(session.results);
  let tab = $state<'css' | 'tw'>('css');
  let copied = $state(false);

  const rows = $derived(
    (r?.sources ?? []).map((s) => {
      const outs = r!.outputs.filter((o) => o.sourceId === s.id);
      return { ...s, outs };
    }),
  );
  const fromBytes = $derived(rows.reduce((a, s) => a + s.size, 0));
  const toBytes = $derived(rows.reduce((a, s) => a + (s.outs.length ? Math.min(...s.outs.map((o) => o.size)) : 0), 0));
  const formatsUsed = $derived([...new Set((r?.outputs ?? []).map((o) => o.format.toUpperCase()))]);
  const anyVariable = $derived((r?.outputs ?? []).some((o) => o.variable));
  const meta = $derived(
    [t('res.meta', { from: fmt.size(fromBytes), to: fmt.size(toBytes), formats: fmt.list(formatsUsed) }), anyVariable ? t('res.axesKept') : '']
      .filter(Boolean)
      .join(' · '),
  );
  const code = $derived(r ? (tab === 'css' ? (r.css ?? '') : tailwindSnippet(r.outputs, t('res.twComment'))) : '');
  const lines = $derived(highlight(code.trimEnd()));
  const ruleCount = $derived(r ? faceRules(r.outputs).length : 0);
  const COLORS = { k: 'text-code-keyword', p: 'text-code-property', s: 'text-code-string', x: 'text-code-text', m: 'text-code-comment' };
  const destShort = $derived(r ? (session.home && r.dest.startsWith(session.home) ? '~' + r.dest.slice(session.home.length) : r.dest) : '');

  async function copy() {
    try {
      await navigator.clipboard.writeText(code);
      copied = true;
      setTimeout(() => (copied = false), 1600);
    } catch {
      copied = false;
    }
  }
</script>

<div class="flex flex-col gap-5 px-[26px] pt-6 pb-[22px]">
  {#if !r}
    <div class="flex flex-col gap-2">
      <h1 class="m-0 font-display text-[31px] leading-[1.15] font-semibold tracking-[-0.01em] text-fg">{t('res.title')}</h1>
    </div>
    <div class="flex min-h-[360px] flex-col items-center justify-center gap-3 rounded-xl border-[1.5px] border-dashed border-accent-dash bg-sunken p-8 text-center">
      <Icon name="layers" size={40} stroke={1.2} class="text-accent-text" />
      <p class="m-0 font-display text-[22px] font-semibold text-fg">{t('res.emptyTitle')}</p>
      <p class="m-0 max-w-md text-fg-muted">{t('res.emptyBody')}</p>
      <button type="button" onclick={() => ui.go('conversion')} class="bg-gold inline-flex min-h-11 items-center gap-2 rounded-[9px] px-4 text-[14.5px] font-semibold">
        <Icon name="convert" size={18} />{t('vf.goConvert')}
      </button>
    </div>
  {:else}
    <div class="flex flex-wrap items-end justify-between gap-3.5">
      <div class="flex min-w-0 flex-col gap-2">
        <h1 class="m-0 font-display text-[31px] leading-[1.15] font-semibold tracking-[-0.01em] text-fg">{t('res.heading', { count: rows.length })}</h1>
        <p class="m-0 text-[14.5px] leading-normal text-fg-muted">{meta}</p>
      </div>
      <div class="flex flex-wrap gap-2.5">
        <button type="button" onclick={() => reveal(r.cssPath ?? r.outputs[0]?.path ?? r.dest)} class="inline-flex min-h-[46px] items-center gap-[9px] rounded-[10px] border border-line-strong px-4 text-[14.5px] font-medium whitespace-nowrap text-fg hover:bg-hover">
          <Icon name="folder" size={18} />
          {t('res.open')}
        </button>
        <button
          type="button"
          onclick={() => {
            session.newSession();
            ui.go('conversion');
          }}
          class="bg-gold inline-flex min-h-[46px] items-center gap-2.5 rounded-[10px] px-5 text-[15px] font-semibold"
        >
          <Icon name="plus" size={19} stroke={1.7} />
          <span class="whitespace-nowrap">{t('res.newConversion')}</span>
        </button>
      </div>
    </div>

    <div class="flex flex-wrap items-start gap-5">
      <section aria-labelledby="files-{id}" class="bg-card shadow-card min-w-0 flex-[1_1_360px] overflow-hidden rounded-xl border border-line">
        <div class="flex items-center gap-2.5 border-b border-line px-[18px] py-4">
          <Icon name="doc" size={19} class="text-fg" />
          <h2 id="files-{id}" class="m-0 text-[15px] font-semibold text-fg">{t('res.files')}</h2>
        </div>
        <ul class="m-0 list-none p-0">
          {#each rows as s (s.id)}
            <li class="flex flex-wrap items-center gap-x-3.5 gap-y-2.5 border-b border-line px-[18px] py-3">
              <span aria-hidden="true" class="flex size-[42px] shrink-0 items-center justify-center rounded-lg border border-line bg-elevated text-[19px] text-fg" style:font-family={s.previewFamily ?? 'inherit'}>Aa</span>
              <span class="flex min-w-0 flex-[1_1_150px] flex-col gap-[3px]">
                <span class="text-[14.5px] font-semibold text-fg">{s.family}</span>
                <span class="text-[12.5px] [overflow-wrap:anywhere] text-fg-muted">{t('res.from', { file: s.name })}</span>
              </span>
              <span class="flex flex-wrap gap-1.5">
                {#each s.outs as o (o.path)}
                  <button type="button" onclick={() => reveal(o.path)} title={o.name} class="inline-flex min-h-[30px] items-center gap-[7px] rounded-[7px] border border-line-strong bg-sunken px-2.5 text-[12.5px] whitespace-nowrap hover:border-fg-muted">
                    <span class="font-semibold text-accent-text">{o.format.toUpperCase()}</span>
                    <span class="text-fg">{fmt.size(o.size)}</span>
                    <span class="font-semibold text-success">{fmt.pct(o.size / s.size - 1)}</span>
                  </button>
                {/each}
              </span>
            </li>
          {/each}
        </ul>
        <div class="flex items-center gap-3.5 px-[18px] py-4">
          <span aria-hidden="true" class="shrink-0 font-display text-[32px] leading-none font-semibold text-accent-text">{fmt.pct(toBytes / Math.max(1, fromBytes) - 1)}</span>
          <span class="text-[13.5px] leading-[1.45] text-fg-muted">
            {t('toast.doneBody', { pct: fmt.pct(toBytes / Math.max(1, fromBytes) - 1), size: fmt.size(toBytes) })}<br />
            {t('res.savedIn', { path: destShort })}
          </span>
        </div>
        {#if r.warnings.length || r.failures.length}
          <div class="flex flex-col gap-2 border-t border-line px-[18px] py-3.5">
            <span class="text-[13px] font-semibold text-fg">{t('res.notes')}</span>
            {#each r.failures as f, i (i)}
              <p class="m-0 flex items-start gap-2 text-[13px] text-error"><Icon name="alert" size={16} />{f.name} · {t(f.error)}</p>
            {/each}
            {#each r.warnings as w, i (i)}
              <p class="m-0 flex items-start gap-2 text-[13px] text-warning">
                <Icon name="info" size={16} />{t(w.code === 'otfVariable' ? 'conv.warnOtfVariable' : 'conv.warnEotStatic', { file: w.file })}
              </p>
            {/each}
          </div>
        {/if}
      </section>

      <section aria-labelledby="code-{id}" class="min-w-0 flex-[1_1_440px] overflow-hidden rounded-xl border border-line bg-sunken">
        <div class="flex flex-wrap items-center gap-1.5 border-b border-line pt-2.5 pr-2.5 pl-3">
          <h2 id="code-{id}" class="sr-only">{t('res.codeTabs')}</h2>
          <div role="tablist" aria-labelledby="code-{id}" class="flex min-w-0 flex-1 gap-1">
            {#each [['css', 'CSS'], ['tw', 'Tailwind v4']] as const as [k, l] (k)}
              <button
                type="button"
                role="tab"
                aria-selected={tab === k}
                onclick={() => {
                  tab = k;
                  copied = false;
                }}
                class="min-h-10 rounded-t-lg px-4 text-[14.5px] whitespace-nowrap {tab === k ? 'bg-selected-soft font-semibold text-fg shadow-[inset_0_-2px_0_var(--ftn-accent)]' : 'text-fg-muted hover:text-fg'}"
              >
                {l}
              </button>
            {/each}
          </div>
          <span class="mb-1.5 text-[12.5px] whitespace-nowrap text-fg-subtle">{t('res.cssRules', { count: ruleCount })}</span>
          <button type="button" onclick={copy} class="mb-1.5 inline-flex min-h-9 items-center gap-[7px] rounded-lg border border-line-strong px-3 text-[13.5px] whitespace-nowrap text-fg hover:bg-hover">
            <Icon name={copied ? 'checkCircle' : 'copy'} size={16} />
            {copied ? t('res.copied') : t('res.copy')}
          </button>
        </div>
        <div role="tabpanel" tabindex="0" aria-label={tab === 'css' ? 'CSS' : 'Tailwind v4'} class="max-h-[520px] overflow-auto py-3.5">
          <pre data-selectable class="m-0 font-mono text-[13px] leading-[1.6] text-code-text">{#each lines as ln, i (i)}<span class="flex gap-4 pr-[18px]"><span aria-hidden="true" class="w-[34px] shrink-0 text-right text-fg-subtle select-none">{i + 1}</span><code class="font-[inherit] whitespace-pre">{#each ln as p, j (j)}<span class={COLORS[p.k]}>{p.text}</span>{/each}</code></span>{/each}</pre>
        </div>
      </section>
    </div>
  {/if}
</div>
