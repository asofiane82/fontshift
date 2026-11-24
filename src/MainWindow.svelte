<script lang="ts">
  import Sidebar from './components/Sidebar.svelte';
  import TabBar from './components/TabBar.svelte';
  import Conversion from './screens/Conversion.svelte';
  import Catalogue from './screens/Catalogue.svelte';
  import Variables from './screens/Variables.svelte';
  import Resultats from './screens/Resultats.svelte';
  import { ui } from './lib/state/ui.svelte';
  import { session } from './lib/state/session.svelte';
  import { engine } from './lib/engine/client.svelte';
  import { onNativeDrop } from './lib/platform';
  import { t } from './lib/i18n/index.svelte';
  import { setWindowTitle } from './lib/platform';

  // Le moteur démarre dès l'ouverture : il est prêt quand les premières polices arrivent.
  engine.start();

  // Glisser-déposer natif sur toute la fenêtre : les polices rejoignent la conversion.
  $effect(() => {
    let off = () => {};
    void onNativeDrop((e) => {
      if (e.type === 'enter' || e.type === 'over') {
        ui.dragging = true;
        if (e.paths.length) ui.dragCount = e.paths.length;
      } else if (e.type === 'leave') {
        ui.dragging = false;
      } else if (e.type === 'drop') {
        ui.dragging = false;
        if (e.paths.length) {
          ui.go('conversion');
          void session.addPaths(e.paths);
        }
      }
    }).then((fn) => (off = fn));
    return () => off();
  });

  $effect(() => {
    void setWindowTitle(t('app.windowMain'));
  });
</script>

<div class="flex h-full bg-app">
  <Sidebar />
  <div class="flex min-w-0 flex-1 flex-col">
    <TabBar />
    <main class="relative min-h-0 flex-1 overflow-x-hidden overflow-y-auto">
      {#if ui.route === 'conversion'}
        <Conversion />
      {:else if ui.route === 'google'}
        <Catalogue />
      {:else if ui.route === 'variables'}
        <Variables />
      {:else}
        <Resultats />
      {/if}
    </main>
  </div>
</div>
