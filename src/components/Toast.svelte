<script lang="ts">
  import Icon from './Icon.svelte';
  import { t } from '../lib/i18n/index.svelte';

  let { title, body, tone = 'success', onclose }: { title: string; body?: string; tone?: 'success' | 'warning' | 'neutral'; onclose: () => void } = $props();

  // Disparition automatique ; un avertissement reste plus longtemps.
  $effect(() => {
    const timer = setTimeout(onclose, tone === 'warning' ? 12000 : 7000);
    return () => clearTimeout(timer);
  });
</script>

<div role="status" class="fixed bottom-[22px] left-[262px] z-50 flex w-[340px] max-w-[calc(100%-52px)] items-start gap-3 rounded-xl border border-line-strong bg-elevated py-3.5 pr-2.5 pl-4 shadow-pop">
  <Icon name={tone === 'success' ? 'checkCircle' : tone === 'warning' ? 'alert' : 'info'} size={22} class={tone === 'success' ? 'text-success' : tone === 'warning' ? 'text-warning' : 'text-fg-muted'} />
  <div class="flex min-w-0 flex-1 flex-col gap-[3px]">
    <span class="text-[14.5px] font-semibold text-fg">{title}</span>
    {#if body}<span class="text-[13px] text-fg-muted">{body}</span>{/if}
  </div>
  <button type="button" onclick={onclose} aria-label={t('toast.close')} title={t('toast.close')} class="flex size-8 shrink-0 items-center justify-center rounded-lg text-fg-muted hover:bg-hover">
    <Icon name="close" size={16} stroke={1.6} />
  </button>
</div>
