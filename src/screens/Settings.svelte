<script lang="ts">
  // Fenêtre des réglages : thème, apparence et langue sont indépendants, enregistrés
  // automatiquement et appliqués aussitôt à toutes les fenêtres.
  import Icon from '../components/Icon.svelte';
  import Select from '../components/Select.svelte';
  import Flag from '../components/Flag.svelte';
  import type { IconName } from '../lib/icons';
  import BrandLogo from '../components/BrandLogo.svelte';
  import { APP_ICON_SVG } from '../lib/brand';
  import { t } from '../lib/i18n/index.svelte';
  import { prefs, THEMES, LANGS, LANG_INFO, DEFAULTS, type LangPref, type ThemeKey } from '../lib/prefs.svelte';
  import { tokens, themeName } from '../lib/theme/palette.js';
  import { isMac, isTauri, setWindowTitle } from '../lib/platform';

  const id = $props.id();
  let tab = $state<'general' | 'appearance' | 'advanced'>('appearance');
  let resetDone = $state(false);
  const version = __APP_VERSION__;

  $effect(() => {
    void setWindowTitle(t('app.windowSettings'));
  });

  const tabs: { key: typeof tab; icon: IconName; label: string }[] = $derived([
    { key: 'general', icon: 'cog', label: t('set.general') },
    { key: 'appearance', icon: 'swatch', label: t('set.appearance') },
    { key: 'advanced', icon: 'shield', label: t('set.advanced') },
  ]);

  const thumbs = $derived(
    THEMES.map((k) => {
      const c = tokens(k, prefs.dark) as Record<string, string>;
      return { key: k as ThemeKey, name: themeName(k), c };
    }),
  );

  const modes = $derived([
    { key: 'light' as const, icon: 'sun' as IconName, label: t('set.light') },
    { key: 'dark' as const, icon: 'moon' as IconName, label: t('set.dark') },
    { key: 'system' as const, icon: 'desktop' as IconName, label: t('set.system') },
  ]);

  const langLabel = (l: LangPref) => (l === 'system' ? t('set.languageSystem', { language: LANG_INFO[prefs.systemLang].native }) : LANG_INFO[l].native);
  const langOptions = $derived((['system', ...LANGS] as LangPref[]).map((l) => ({ id: l, label: langLabel(l) })));
  const flagOf = (l: LangPref) => LANG_INFO[l === 'system' ? prefs.systemLang : l].flag;

  const set = <K extends 'theme' | 'appearance' | 'lang'>(k: K, v: (typeof prefs)[K]) => {
    prefs.set(k, v);
    resetDone = false;
  };
  const stored = $derived([
    { label: t('set.theme'), value: themeName(prefs.theme), key: 'fontaine.theme' },
    { label: t('set.mode'), value: t('set.' + prefs.appearance), key: 'fontaine.appearance' },
    { label: t('set.language'), value: langLabel(prefs.lang), key: 'fontaine.lang' },
  ]);

</script>

<div class="flex h-full flex-col bg-app">
  <header class="grid h-[52px] shrink-0 grid-cols-[1fr_auto_1fr] items-center bg-tabbar px-3.5" data-tauri-drag-region>
    <span data-tauri-drag-region class={isMac && isTauri ? 'w-20' : ''}></span>
    <h1 class="m-0 text-[15px] font-semibold whitespace-nowrap text-fg" data-tauri-drag-region>{t('set.title')}</h1>
    <span></span>
  </header>

  <div role="tablist" aria-label={t('set.tabs')} class="flex shrink-0 flex-wrap justify-center gap-1.5 border-b border-line bg-tabbar px-4 pt-1 pb-3" data-tauri-drag-region>
    {#each tabs as tb (tb.key)}
      <button
        type="button"
        role="tab"
        aria-selected={tab === tb.key}
        onclick={() => (tab = tb.key)}
        class="flex min-h-16 min-w-[104px] flex-col items-center justify-center gap-[5px] rounded-[10px] px-3.5 py-1.5 text-[13.5px] {tab === tb.key ? 'bg-selected font-semibold text-fg' : 'font-medium text-fg-muted hover:text-fg'}"
      >
        <Icon name={tb.icon} size={22} />
        <span class="whitespace-nowrap">{tb.label}</span>
      </button>
    {/each}
  </div>

  <div role="tabpanel" aria-label={tabs.find((x) => x.key === tab)?.label} class="min-h-0 flex-1 overflow-auto">
    <div class="mx-auto flex max-w-[760px] flex-col gap-7 px-8 pt-[26px] pb-7">
      {#if tab === 'appearance'}
        <section aria-labelledby="th-{id}" class="flex flex-col gap-3.5">
          <div class="flex flex-col gap-1">
            <h2 id="th-{id}" class="m-0 text-[15px] font-semibold text-fg">{t('set.theme')}</h2>
            <p class="m-0 text-[13.5px] text-fg-muted">{t('set.themeDesc')}</p>
          </div>
          <div role="radiogroup" aria-labelledby="th-{id}" class="grid grid-cols-2 gap-3.5">
            {#each thumbs as th (th.key)}
              {@const on = prefs.theme === th.key}
              <button
                type="button"
                role="radio"
                aria-checked={on}
                onclick={() => set('theme', th.key)}
                class="flex flex-col gap-2.5 rounded-xl px-2 pt-2 pb-2.5 text-left {on ? 'ring-sel border-[1.5px] border-accent bg-selected-soft' : 'border-[1.5px] border-line bg-surface hover:border-line-strong'}"
              >
                <span aria-hidden="true" class="flex h-28 overflow-hidden rounded-lg border" style:background={th.c.backgroundFill} style:border-color={th.c.border}>
                  <span class="flex w-[30%] shrink-0 flex-col gap-[7px] border-r px-[9px] py-2.5" style:background={th.c.sidebar} style:border-color={th.c.border}>
                    <span class="mb-[3px] flex" style:color={th.c.textPrimary} style:--ftn-brand-gold={th.c.brandGold}><BrandLogo variant="monogram" height={17} /></span>
                    <span class="block h-1.5 w-[90%] rounded-[3px]" style:background={th.c.accentText}></span>
                    <span class="block h-1.5 w-[70%] rounded-[3px]" style:background={th.c.border}></span>
                    <span class="block h-1.5 w-[70%] rounded-[3px]" style:background={th.c.border}></span>
                  </span>
                  <span class="flex min-w-0 flex-1 flex-col gap-[7px] px-2.5 py-3">
                    <span class="block h-[7px] w-[58%] rounded-[3px]" style:background={th.c.textPrimary}></span>
                    <span class="flex flex-1 items-center justify-center rounded-[5px] border border-dashed" style:border-color={th.c.accentDash} style:background={th.c.surfaceSunken}>
                      <span class="block h-[9px] w-[42%] rounded-[3px]" style:background={th.c.accentFill}></span>
                    </span>
                    <span class="block h-[18px] rounded border" style:background={th.c.surface} style:border-color={th.c.border}></span>
                  </span>
                </span>
                <span class="flex items-center gap-2 px-1">
                  <span class="min-w-0 text-[14px] font-semibold text-fg">{th.name}</span>
                  {#if th.key === DEFAULTS.theme}
                    <span class="shrink-0 rounded-md bg-badge px-[7px] py-0.5 text-[11.5px] font-medium whitespace-nowrap text-fg-muted">{t('set.themeDefault')}</span>
                  {/if}
                  <span class="flex-1"></span>
                  <span class="flex size-5 shrink-0 items-center justify-center rounded-full {on ? 'bg-gold-flat' : 'border-[1.5px] border-line-strong'}">
                    {#if on}<Icon name="check" size={13} />{/if}
                  </span>
                </span>
              </button>
            {/each}
          </div>
        </section>

        <section aria-labelledby="md-{id}" class="flex flex-col gap-3.5">
          <div class="flex flex-col gap-1">
            <h2 id="md-{id}" class="m-0 text-[15px] font-semibold text-fg">{t('set.mode')}</h2>
            <p class="m-0 text-[13.5px] text-fg-muted">{t('set.modeDesc')}</p>
          </div>
          <div role="radiogroup" aria-labelledby="md-{id}" class="grid grid-cols-3 gap-1 rounded-xl border border-line bg-sunken p-1">
            {#each modes as m (m.key)}
              {@const on = prefs.appearance === m.key}
              <button
                type="button"
                role="radio"
                aria-checked={on}
                onclick={() => set('appearance', m.key)}
                class="flex min-h-11 items-center justify-center gap-[9px] rounded-[9px] px-3 text-[14.5px] {on ? 'bg-gold font-semibold' : 'font-medium text-fg-muted hover:text-fg'}"
              >
                <Icon name={m.icon} size={19} />
                <span class="whitespace-nowrap">{m.label}</span>
              </button>
            {/each}
          </div>
        </section>

        <section aria-labelledby="lg-{id}" class="flex flex-col gap-3.5">
          <div class="flex flex-col gap-1">
            <h2 id="lg-{id}" class="m-0 text-[15px] font-semibold text-fg">{t('set.language')}</h2>
            <p class="m-0 text-[13.5px] text-fg-muted">{t('set.languageDesc')}</p>
          </div>
          <div class="max-w-[380px]">
            <Select value={prefs.lang} options={langOptions} labelledby="lg-{id}" menuWidth="w-full" align="left" triggerClass="min-h-[46px] rounded-[10px] gap-3 pl-3.5" onchange={(v) => set('lang', v)}>
              {#snippet lead()}
                {#if prefs.lang === 'system'}
                  <Icon name="desktop" size={20} class="text-fg-muted" />
                {:else}
                  <Flag code={flagOf(prefs.lang)} />
                {/if}
              {/snippet}
              {#snippet optionLead(o)}
                {#if o.id === 'system'}
                  <span class="mx-0.5"><Icon name="desktop" size={20} class="text-fg-muted" /></span>
                {:else}
                  <Flag code={flagOf(o.id)} />
                {/if}
              {/snippet}
            </Select>
          </div>
          <p class="m-0 flex items-center gap-2 text-[13px] text-fg-muted">
            <Icon name="info" size={17} class="text-accent-text" />
            {t('set.languageNote')}
          </p>
        </section>
      {:else if tab === 'general'}
        <section aria-labelledby="ab-{id}" class="flex flex-col gap-4">
          <h2 id="ab-{id}" class="m-0 text-[15px] font-semibold text-fg">{t('set.about')}</h2>
          <div class="bg-card shadow-card flex flex-wrap items-center gap-[22px] rounded-xl border border-line p-[22px]">
            <span role="img" aria-label={t('set.iconAria')} class="block size-[104px] shrink-0 [&>svg]:size-full">{@html APP_ICON_SVG}</span>
            <div class="flex min-w-0 flex-[1_1_220px] flex-col gap-1.5">
              <span class="text-fg"><BrandLogo variant="wordmark" height={34} label={t('app.name')} /></span>
              <span class="text-[14px] text-fg-muted">{t('app.version', { version })}</span>
              <span class="text-[14px] text-fg-muted">{t('set.platforms')}</span>
            </div>
          </div>
          <p class="m-0 flex items-start gap-2.5 rounded-[10px] border border-line bg-sunken px-4 py-3.5 text-[13.5px] leading-normal text-fg-muted">
            <Icon name="shield" size={19} class="text-accent-text" />
            {t('set.local')}
          </p>
        </section>
      {:else}
        <section aria-labelledby="pr-{id}" class="flex flex-col gap-3.5">
          <h2 id="pr-{id}" class="m-0 text-[15px] font-semibold text-fg">{t('set.prefsStored')}</h2>
          <dl class="bg-card m-0 overflow-hidden rounded-xl border border-line">
            {#each stored as p (p.key)}
              <div class="flex flex-wrap items-center gap-x-4 gap-y-1.5 border-b border-line px-[18px] py-3.5 last:border-b-0">
                <dt class="flex-[1_1_140px] text-[14px] text-fg-muted">{p.label}</dt>
                <dd class="m-0 flex flex-wrap items-center gap-3">
                  <span class="text-[14.5px] font-semibold text-fg">{p.value}</span>
                  <code class="rounded-md border border-line bg-sunken px-2 py-[3px] font-mono text-[12.5px] text-code-text">{p.key}</code>
                </dd>
              </div>
            {/each}
          </dl>
          <p class="m-0 text-[13.5px] leading-normal text-fg-muted">{t('set.resetDesc')}</p>
        </section>
      {/if}
    </div>
  </div>

  <footer class="flex shrink-0 flex-wrap items-center justify-between gap-x-4 gap-y-2.5 border-t border-line bg-tabbar py-3 pr-6 pl-8">
    <p role="status" class="m-0 flex items-center gap-2 text-[13.5px] text-fg-muted">
      <Icon name="checkCircle" size={18} class="text-success" />
      {resetDone ? t('toast.resetDone') : t('set.autosave')}
    </p>
    <button
      type="button"
      title={t('set.resetDesc')}
      onclick={() => {
        prefs.reset();
        resetDone = true;
      }}
      class="inline-flex min-h-11 items-center gap-2 rounded-[10px] border border-line-strong px-4 text-[14px] font-medium whitespace-nowrap text-fg hover:bg-hover"
    >
      <Icon name="replay" size={17} />
      {t('set.reset')}
    </button>
  </footer>
</div>
