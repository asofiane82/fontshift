<script lang="ts">
  import Icon from './Icon.svelte';
  import { t } from '../lib/i18n/index.svelte';

  let { topic, text }: { topic: string; text: string } = $props();
  let open = $state(false);
  const id = $props.id();
</script>

<span class="relative shrink-0">
  <button
    type="button"
    aria-label={t('conv.infoAria', { topic })}
    aria-describedby={open ? 'tip-' + id : undefined}
    onmouseenter={() => (open = true)}
    onmouseleave={() => (open = false)}
    onfocus={() => (open = true)}
    onblur={() => (open = false)}
    onclick={() => (open = !open)}
    class="flex size-8 items-center justify-center rounded-full text-fg-muted hover:bg-hover hover:text-fg"
  >
    <Icon name="info" size={19} />
  </button>
  {#if open}
    <span id="tip-{id}" role="tooltip" class="absolute right-0 bottom-[calc(100%+6px)] z-40 w-64 rounded-[10px] border border-line-strong bg-elevated px-3 py-2.5 text-[13px] leading-snug text-fg-muted shadow-pop">
      {text}
    </span>
  {/if}
</span>
