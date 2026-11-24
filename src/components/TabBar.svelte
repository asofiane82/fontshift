<script lang="ts">
  import { t } from '../lib/i18n/index.svelte';
  import { ui } from '../lib/state/ui.svelte';

  const titles = { conversion: 'nav.conversion', google: 'nav.google', variables: 'nav.variables', results: 'res.title' } as const;
</script>

<!-- Barre du haut : nom de l'écran actif ; sert aussi à déplacer la fenêtre. Les actions sont dans la barre latérale. -->
<header class="flex h-[52px] shrink-0 items-end gap-1.5 border-b border-line bg-tabbar pr-3 pl-3.5" data-tauri-drag-region>
  <div role="tablist" aria-label={t('top.tabs')} class="flex">
    <span role="tab" aria-selected="true" class="-mb-px flex h-[42px] items-center rounded-t-[10px] border border-line border-b-tab-active bg-tab-active px-7 text-[15px] font-medium whitespace-nowrap text-fg">
      {t(titles[ui.route])}
    </span>
  </div>
  <div class="flex-1 self-stretch" data-tauri-drag-region></div>
</header>
