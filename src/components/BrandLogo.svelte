<script lang="ts">
  // Logo Fontaine vectoriel. La forme haute reste or (--ftn-brand-gold) ; la forme basse et le
  // logotype prennent la couleur du texte courant, ce qui garde le logo lisible dans tous les thèmes.
  import { MONOGRAM, WORDMARK, LOGO } from '../lib/brand';

  let {
    variant = 'lockup',
    height = 40,
    label,
    class: klass = '',
  }: { variant?: 'lockup' | 'monogram' | 'wordmark'; height?: number; label?: string; class?: string } = $props();

  // Cadrage de chaque variante dans le repère du logo (hauteur du monogramme = 100).
  const view = $derived(
    variant === 'monogram'
      ? { x: 0, y: 0, w: MONOGRAM.w, h: MONOGRAM.h }
      : variant === 'wordmark'
        ? { x: WORDMARK.x, y: WORDMARK.capTop - 3.5, w: WORDMARK.w, h: WORDMARK.baseline - WORDMARK.capTop + 4.2 }
        : { x: 0, y: 0, w: LOGO.w, h: LOGO.h },
  );
  const width = $derived((height * view.w) / view.h);
</script>

<svg
  role={label ? 'img' : undefined}
  aria-label={label}
  aria-hidden={label ? undefined : 'true'}
  width={width}
  {height}
  viewBox="{view.x} {view.y} {view.w} {view.h}"
  class="shrink-0 {klass}"
>
  {#if variant !== 'wordmark'}
    <path fill="currentColor" d={MONOGRAM.lower} />
    <path fill="var(--ftn-brand-gold)" d={MONOGRAM.upper} />
  {/if}
  {#if variant !== 'monogram'}
    <path fill="currentColor" d={WORDMARK.d} />
  {/if}
</svg>
