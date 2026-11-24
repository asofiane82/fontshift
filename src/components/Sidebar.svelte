<script lang="ts">
  import Icon from './Icon.svelte';
  import BrandLogo from './BrandLogo.svelte';
  import { WORDMARK } from '../lib/brand';
  import type { IconName } from '../lib/icons';
  import { t, fmt } from '../lib/i18n/index.svelte';
  import { ui, type Route } from '../lib/state/ui.svelte';
  import { session } from '../lib/state/session.svelte';
  import { isMac, isTauri, openSettingsWindow } from '../lib/platform';

  const LOGO_H = 44;
  const resultCount = $derived(session.results?.sources.length ?? 0);
  const items: { key: Route; icon: IconName; label: () => string }[] = [
    { key: 'conversion', icon: 'convert', label: () => t('nav.conversion') },
    { key: 'google', icon: 'google', label: () => t('nav.google') },
    { key: 'variables', icon: 'variables', label: () => t('nav.variables') },
    { key: 'results', icon: 'layers', label: () => t('nav.results') },
  ];
  const go = (r: Route) => {
    ui.go(r);
    if (r === 'results') session.unseen = false;
  };
</script>

<aside class="flex w-[236px] shrink-0 flex-col border-r border-line bg-sidebar">
  <!-- Les boutons de fenêtre macOS se placent ici (barre de titre transparente). -->
  <div class={isMac && isTauri ? 'h-[52px] shrink-0' : 'h-4 shrink-0'} data-tauri-drag-region></div>
  <div class="flex flex-col gap-1.5 px-5 pt-2.5 text-fg" data-tauri-drag-region>
    <BrandLogo height={LOGO_H} label={t('app.name')} />
    <!-- slogan aligné sur le début du logotype -->
    <span class="text-[13px] leading-tight text-fg-muted" style:padding-left="{(WORDMARK.x * LOGO_H) / 100}px" data-tauri-drag-region>{t('app.tagline')}</span>
  </div>
  <nav aria-label={t('nav.main')} class="flex flex-col gap-1 px-3.5 pt-[30px]">
    {#each items as item (item.key)}
      {@const on = ui.route === item.key}
      <button
        type="button"
        aria-current={on ? 'page' : undefined}
        onclick={() => go(item.key)}
        class="flex min-h-11 items-center gap-3.5 rounded-[9px] pr-3 pl-3.5 text-left text-[15px] text-fg {on ? 'bg-selected font-semibold' : 'font-normal hover:bg-hover'}"
      >
        <Icon name={item.icon} size={20} />
        <span class="min-w-0 flex-1 truncate">{item.label()}</span>
        {#if item.key === 'results' && resultCount > 0}
          <span aria-label={t('nav.resultsBadge', { count: resultCount })} class="min-w-6 shrink-0 rounded-md bg-badge px-[7px] py-0.5 text-center text-[12px] font-semibold text-fg">{fmt.num(resultCount)}</span>
        {/if}
      </button>
    {/each}
  </nav>
  <div class="min-h-6 flex-1" data-tauri-drag-region></div>
  <div class="px-3.5 pb-[18px]">
    <button type="button" onclick={() => openSettingsWindow(t('app.windowSettings'))} class="flex min-h-11 w-full items-center gap-3.5 rounded-[9px] px-3.5 text-left text-[15px] text-fg hover:bg-hover">
      <Icon name="cog" size={20} />
      <span class="truncate">{t('nav.settings')}</span>
    </button>
  </div>
</aside>
