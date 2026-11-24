<script lang="ts">
  // Aperçu « Ag » : la police choisie avec ses lignes de référence réelles ;
  // sans police, le spécimen anatomique de la référence visuelle (Playfair Display).
  import { glyphs } from '../lib/glyphs';
  import { t } from '../lib/i18n/index.svelte';
  import type { FontItem } from '../lib/state/session.svelte';

  let { item }: { item: FontItem | null } = $props();

  const W = 500;
  const H = 260;

  type Guide = { key: string; y: number; side: 'left' | 'right' };

  const view = $derived.by(() => {
    const info = item?.info;
    if (!item || !info || !item.previewFamily) return null;
    const m = info.metrics;
    const top = Math.max(m.ascenderGlyph, m.capHeight, m.xHeight + 1);
    const bottom = Math.min(m.descenderGlyph, -1);
    const fs = (m.unitsPerEm * 196) / (top - bottom);
    const k = fs / m.unitsPerEm;
    const baseline = 32 + top * k;
    const y = (v: number) => baseline - v * k;
    const guides: Guide[] = [];
    if (Math.abs(m.ascenderGlyph - m.capHeight) > m.unitsPerEm * 0.03) guides.push({ key: 'ascender', y: y(m.ascenderGlyph), side: 'right' });
    guides.push({ key: 'capHeight', y: y(m.capHeight), side: 'left' });
    guides.push({ key: 'xHeight', y: y(m.xHeight), side: 'left' });
    guides.push({ key: 'baseline', y: baseline, side: 'left' });
    guides.push({ key: 'descender', y: y(m.descenderGlyph), side: 'right' });
    // Étiquettes espacées d'au moins 18 px de chaque côté ; le trait d'appel rejoint la ligne.
    for (const side of ['left', 'right'] as const) {
      const list = guides.filter((g) => g.side === side).sort((a, b) => a.y - b.y);
      let last = -Infinity;
      for (const g of list) {
        (g as Guide & { ly: number }).ly = Math.max(g.y, last + 18);
        last = (g as Guide & { ly: number }).ly;
      }
    }
    return { fs, baseline, guides: guides as (Guide & { ly: number })[], family: item.previewFamily, name: info.fullName || info.family };
  });
</script>

{#if view}
  <svg role="img" aria-label={t('conv.metricsAria', { name: view.name })} viewBox="0 0 {W} {H}" class="block h-auto w-full max-w-[520px]">
    <g fill="none" stroke="var(--ftn-leader)" stroke-width="0.8" stroke-dasharray="3 3">
      {#each view.guides as g (g.key)}
        <line x1="140" y1={g.y} x2="360" y2={g.y} />
      {/each}
    </g>
    <text x={W / 2} y={view.baseline} text-anchor="middle" font-family={view.family} font-size={view.fs} fill="var(--ftn-specimen)">Ag</text>
    <g fill="none" stroke="var(--ftn-leader)" stroke-width="0.8">
      {#each view.guides as g (g.key)}
        {#if g.side === 'left'}
          <polyline points="134,{g.ly} 137,{g.ly} 140,{g.y}" />
        {:else}
          <polyline points="366,{g.ly} 363,{g.ly} 360,{g.y}" />
        {/if}
      {/each}
    </g>
    <g fill="var(--ftn-accent)" stroke="var(--ftn-surface-sunken)" stroke-width="1.5">
      {#each view.guides as g (g.key)}
        <circle cx={g.side === 'left' ? 140 : 360} cy={g.y} r="3.4" />
      {/each}
    </g>
    <g fill="var(--ftn-text-primary)" font-family="var(--font-sans)" font-size="13">
      {#each view.guides as g (g.key)}
        <text x={g.side === 'left' ? 130 : 370} y={g.ly + 4} text-anchor={g.side === 'left' ? 'end' : 'start'}>{t('conv.metrics.' + g.key)}</text>
      {/each}
    </g>
  </svg>
{:else}
  <svg role="img" aria-label={t('conv.specimenAria')} viewBox="0 0 {W} {H}" class="block h-auto w-full max-w-[520px]">
    <path d={glyphs.ag} fill="var(--ftn-specimen)" />
    <g fill="none" stroke="var(--ftn-leader)" stroke-width="0.8">
      <polyline points="108,66 140,66 167.6,116" />
      <polyline points="108,136 164.4,136 164.4,140" stroke-dasharray="2 2" />
      <polyline points="108,224 118,224 129,197" />
      <polyline points="392,58 380,58 368,94" />
      <polyline points="392,136 362,136 343.8,120" />
      <polyline points="392,224 372,224 341.4,230" />
    </g>
    <g fill="var(--ftn-accent)" stroke="var(--ftn-surface-sunken)" stroke-width="1.5">
      <circle cx="167.6" cy="116" r="3.4" />
      <circle cx="164.4" cy="140" r="3.4" />
      <circle cx="129" cy="197" r="3.4" />
      <circle cx="368" cy="94" r="3.4" />
      <circle cx="343.8" cy="120" r="3.4" />
      <circle cx="341.4" cy="230" r="3.4" />
    </g>
    <g fill="var(--ftn-text-primary)" font-family="var(--font-sans)" font-size="13">
      <text x="102" y="70" text-anchor="end">{t('conv.anatomy.stem')}</text>
      <text x="102" y="140" text-anchor="end">{t('conv.anatomy.eye')}</text>
      <text x="102" y="228" text-anchor="end">{t('conv.anatomy.serif')}</text>
      <text x="398" y="62">{t('conv.anatomy.ascender')}</text>
      <text x="398" y="140">{t('conv.anatomy.axis')}</text>
      <text x="398" y="228">{t('conv.anatomy.descender')}</text>
    </g>
  </svg>
{/if}
