<script lang="ts">
  import MainWindow from './MainWindow.svelte';
  import SettingsWindow from './screens/Settings.svelte';
  import { applyToDocument } from './lib/prefs.svelte';

  applyToDocument();
  const isSettings = new URLSearchParams(location.search).get('window') === 'settings';
</script>

{#if isSettings}
  <SettingsWindow />
{:else}
  <MainWindow />
{/if}
