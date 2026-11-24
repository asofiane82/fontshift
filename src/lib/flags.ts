// Drapeaux des langues, dessinés dans une boîte 60 × 40 (couleurs officielles, hors thème).
type Rect = { x: number; y: number; w: number; h: number; fill: string };
type Line = { x1: number; y1: number; x2: number; y2: number; stroke: string; sw: number };

const W = 60;
const H = 40;

export function flagShapes(code: 'fr' | 'gb' | 'es'): { rects: Rect[]; lines: Line[] } {
  if (code === 'fr') {
    return { rects: ['#0055A4', '#FFFFFF', '#EF4135'].map((fill, i) => ({ x: (i * W) / 3, y: 0, w: W / 3, h: H, fill })), lines: [] };
  }
  if (code === 'es') {
    return {
      rects: [
        { x: 0, y: 0, w: W, h: H * 0.25, fill: '#AA151B' },
        { x: 0, y: H * 0.25, w: W, h: H * 0.5, fill: '#F1BF00' },
        { x: 0, y: H * 0.75, w: W, h: H * 0.25, fill: '#AA151B' },
      ],
      lines: [],
    };
  }
  const diag = [
    [0, 0, W, H],
    [W, 0, 0, H],
  ];
  const cross = [
    [0, H / 2, W, H / 2],
    [W / 2, 0, W / 2, H],
  ];
  const ln = (set: number[][], stroke: string, sw: number) => set.map(([x1, y1, x2, y2]) => ({ x1, y1, x2, y2, stroke, sw }));
  return {
    rects: [{ x: 0, y: 0, w: W, h: H, fill: '#012169' }],
    lines: [...ln(diag, '#FFFFFF', 8), ...ln(diag, '#C8102E', 2.6), ...ln(cross, '#FFFFFF', 12), ...ln(cross, '#C8102E', 7)],
  };
}
