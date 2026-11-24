<script lang="ts" generics="T extends string">
  import type { Snippet } from 'svelte';
  import Icon from './Icon.svelte';
  import { t } from '../lib/i18n/index.svelte';

  type Option = { id: T; label: string; hint?: string };
  let {
    value,
    options,
    onchange,
    labelledby,
    width = 'w-full',
    menuWidth = 'w-[300px]',
    align = 'right',
    lead,
    optionLead,
    triggerClass = '',
  }: {
    value: T;
    options: Option[];
    onchange: (v: T) => void;
    labelledby: string;
    width?: string;
    menuWidth?: string;
    align?: 'left' | 'right';
    lead?: Snippet;
    optionLead?: Snippet<[Option]>;
    triggerClass?: string;
  } = $props();

  let open = $state(false);
  let active = $state(0);
  let trigger: HTMLButtonElement | undefined = $state();
  let list: HTMLDivElement | undefined = $state();
  const id = $props.id();
  const current = $derived(options.find((o) => o.id === value) ?? options[0]);

  function show() {
    open = true;
    active = Math.max(0, options.findIndex((o) => o.id === value));
    queueMicrotask(() => list?.focus());
  }
  function close(refocus = true) {
    open = false;
    if (refocus) trigger?.focus();
  }
  function pick(o: Option) {
    onchange(o.id);
    close();
  }
  function onKey(e: KeyboardEvent) {
    if (e.key === 'ArrowDown') active = Math.min(options.length - 1, active + 1);
    else if (e.key === 'ArrowUp') active = Math.max(0, active - 1);
    else if (e.key === 'Home') active = 0;
    else if (e.key === 'End') active = options.length - 1;
    else if (e.key === 'Enter' || e.key === ' ') pick(options[active]);
    else if (e.key === 'Escape' || e.key === 'Tab') return close(e.key === 'Escape');
    else return;
    e.preventDefault();
  }
</script>

<div class="relative {width}">
  <button
    bind:this={trigger}
    type="button"
    aria-haspopup="listbox"
    aria-expanded={open}
    aria-labelledby="{labelledby} val-{id}"
    onclick={() => (open ? close() : show())}
    onkeydown={(e) => (e.key === 'ArrowDown' || e.key === 'ArrowUp') && (e.preventDefault(), show())}
    class="flex min-h-10 w-full items-center gap-2 rounded-lg border bg-elevated pr-2.5 pl-3 text-left text-[14px] text-fg {open ? 'border-focus ring-sel' : 'border-line-strong'} {triggerClass}"
  >
    {@render lead?.()}
    <span id="val-{id}" class="min-w-0 flex-1 truncate">{current?.label}</span>
    <Icon name="chevron" size={17} class="text-fg-muted transition-transform duration-200 {open ? 'rotate-180' : ''}" />
  </button>
  {#if open}
    <button type="button" tabindex="-1" aria-label={t('conv.closeList')} class="fixed inset-0 z-30 cursor-default" onclick={() => close(false)}></button>
    <div
      bind:this={list}
      role="listbox"
      tabindex="-1"
      aria-labelledby={labelledby}
      aria-activedescendant="opt-{id}-{active}"
      onkeydown={onKey}
      class="absolute top-[calc(100%+6px)] z-40 flex max-w-[80vw] flex-col gap-0.5 rounded-[10px] border border-line-strong bg-elevated p-1.5 shadow-pop outline-none {menuWidth} {align === 'right' ? 'right-0' : 'left-0'}"
    >
      {#each options as o, i (o.id)}
        <div
          id="opt-{id}-{i}"
          role="option"
          tabindex="-1"
          aria-selected={o.id === value}
          onclick={() => pick(o)}
          onkeydown={() => {}}
          onmouseenter={() => (active = i)}
          class="flex items-center gap-3 rounded-[7px] px-2.5 py-[7px] {o.hint ? 'min-h-[52px]' : 'min-h-11'} {o.id === value ? 'bg-selected-soft' : i === active ? 'bg-hover' : ''}"
        >
          {@render optionLead?.(o)}
          <span class="flex min-w-0 flex-1 flex-col gap-0.5">
            <span class="text-[14px] font-medium text-fg">{o.label}</span>
            {#if o.hint}<span class="text-[12.5px] text-fg-subtle">{o.hint}</span>{/if}
          </span>
          <span class="size-[18px] shrink-0 text-accent-text">
            {#if o.id === value}<Icon name="check" size={18} />{/if}
          </span>
        </div>
      {/each}
    </div>
  {/if}
</div>
