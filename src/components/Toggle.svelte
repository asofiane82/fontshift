<script lang="ts">
  let { checked, onchange, labelledby, label, disabled = false }: { checked: boolean; onchange: (v: boolean) => void; labelledby?: string; label?: string; disabled?: boolean } = $props();
</script>

<button
  type="button"
  role="switch"
  aria-checked={checked}
  aria-labelledby={labelledby}
  aria-label={label}
  {disabled}
  onclick={() => onchange(!checked)}
  class="flex h-10 w-[52px] shrink-0 items-center justify-center rounded-lg disabled:cursor-not-allowed disabled:opacity-40"
>
  <span
    aria-hidden="true"
    class="relative block h-6 w-10 rounded-full transition-colors {checked ? 'bg-gold-flat' : 'border border-line-strong bg-elevated'}"
  >
    <span
      class="absolute top-[3px] size-[18px] rounded-full shadow-[0_1px_2px_rgb(0_0_0/0.25)] transition-[left] duration-150 {checked ? 'left-[19px] bg-knob' : 'left-[3px] bg-fg-subtle'}"
    ></span>
  </span>
</button>
