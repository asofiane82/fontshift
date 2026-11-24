<script lang="ts">
  import Icon from './Icon.svelte';
  import { t } from '../lib/i18n/index.svelte';
  import { ui } from '../lib/state/ui.svelte';
  import { session } from '../lib/state/session.svelte';
  import { openSettingsWindow } from '../lib/platform';

  const titles = { conversion: 'nav.conversion', google: 'nav.google', variables: 'nav.variables', results: 'res.title' } as const;
  const iconBtn = 'flex size-11 items-center justify-center rounded-lg text-fg hover:bg-hover';
</script>

<header class="flex h-[52px] shrink-0 items-end gap-1.5 border-b border-line bg-tabbar pr-3 pl-3.5" data-tauri-drag-region>
  <div role="tablist" aria-label={t('top.tabs')} class="flex">
    <span role="tab" aria-selected="true" class="-mb-px flex h-[42px] items-center rounded-t-[10px] border border-line border-b-tab-active bg-tab-active px-7 text-[15px] font-medium whitespace-nowrap text-fg">
      {t(titles[ui.route])}
    </span>
  </div>
  <button
    type="button"
    onclick={() => {
      session.newSession();
      ui.go('conversion');
    }}
    aria-label={t('top.newSession')}
    title={t('top.newSession')}
    class="flex size-11 items-center justify-center self-center rounded-lg text-fg-muted hover:bg-hover hover:text-fg"
  >
    <Icon name="plus" size={20} />
  </button>
  <div class="flex-1 self-stretch" data-tauri-drag-region></div>
  <div class="flex gap-0.5 self-center">
    <button type="button" onclick={() => ui.go('google')} aria-label={t('top.search')} title={t('top.search')} class={iconBtn}>
      <Icon name="search" size={21} />
    </button>
    <button
      type="button"
      onclick={() => {
        session.unseen = false;
        ui.go('results');
      }}
      aria-label={t('top.notifications')}
      title={t('top.notifications')}
      class="relative {iconBtn}"
    >
      <Icon name="bell" size={21} />
      {#if session.unseen}
        <span aria-hidden="true" class="absolute top-[11px] right-3 size-[7px] rounded-full bg-accent shadow-[0_0_0_2px_var(--ftn-tabbar)]"></span>
      {/if}
    </button>
    <button type="button" onclick={() => openSettingsWindow(t('app.windowSettings'))} aria-label={t('top.more')} title={t('top.more')} class={iconBtn}>
      <Icon name="more" size={21} />
    </button>
  </div>
</header>
