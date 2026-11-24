<script lang="ts">
  import { icons, type IconName } from '../lib/icons';

  let { name, size = 20, stroke = 1.5, class: cls = '' }: { name: IconName; size?: number; stroke?: number; class?: string } = $props();
  // check et chevron sont des icônes « mini » pleines (20 px) ; les autres sont au trait (24 px).
  const solid = $derived(name === 'check' || name === 'chevron');
</script>

{#if solid}
  <svg aria-hidden="true" width={size} height={size} viewBox="0 0 20 20" fill="currentColor" class="shrink-0 {cls}">
    <path fill-rule="evenodd" clip-rule="evenodd" d={icons[name]} />
  </svg>
{:else}
  <svg aria-hidden="true" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width={stroke} class="shrink-0 {cls}">
    <path stroke-linecap="round" stroke-linejoin="round" d={icons[name]} />
  </svg>
{/if}
