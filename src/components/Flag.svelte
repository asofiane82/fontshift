<script lang="ts">
  import { flagShapes } from '../lib/flags';

  let { code, width = 24 }: { code: 'fr' | 'gb' | 'es'; width?: number } = $props();
  const shapes = $derived(flagShapes(code));
</script>

<svg aria-hidden="true" width={width} height={(width * 2) / 3} viewBox="0 0 60 40" preserveAspectRatio="none" class="shrink-0 overflow-hidden rounded-[3px] shadow-[0_0_0_1px_var(--ftn-border)]">
  {#each shapes.rects as r, i (i)}
    <rect x={r.x} y={r.y} width={r.w} height={r.h} fill={r.fill} />
  {/each}
  {#each shapes.lines as l, i (i)}
    <line x1={l.x1} y1={l.y1} x2={l.x2} y2={l.y2} stroke={l.stroke} stroke-width={l.sw} />
  {/each}
</svg>
