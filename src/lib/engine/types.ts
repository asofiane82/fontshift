export interface Axis {
  tag: string;
  name: string;
  min: number;
  default: number;
  max: number;
  hidden: boolean;
}

export interface NamedInstance {
  name: string;
  coords: Record<string, number>;
}

export interface Metrics {
  unitsPerEm: number;
  ascender: number;
  descender: number;
  ascenderGlyph: number;
  descenderGlyph: number;
  capHeight: number;
  xHeight: number;
}

export interface FaceInfo {
  family: string;
  style: string;
  fullName: string;
  postscriptName: string;
  version: string;
  sourceFormat: 'TTF' | 'OTF' | 'WOFF' | 'WOFF2' | 'TTC' | 'EOT';
  flavor: string;
  outlines: 'TrueType' | 'CFF' | 'CFF2' | 'Bitmap';
  glyphs: number;
  codepoints: number;
  variable: boolean;
  axes: Axis[];
  instances: NamedInstance[];
  weight: number;
  widthClass: number;
  italic: boolean;
  tables: string[];
  metrics: Metrics;
  sample: string[];
  extracted?: Uint8Array;
  index: number;
}

export type EngineErrorCode = 'type1' | 'unknownFormat' | 'corrupt' | 'eotCompressed' | 'noFormat' | 'convertFailed';

export type MergeErrorCode = 'mergeIncompatible' | 'mergeGlyphSet' | 'mergeSameStyle' | 'mergeMixed' | 'mergeVariable' | 'mergeTooFew' | 'mergeFailed' | EngineErrorCode;

export interface OpenResult {
  faces?: FaceInfo[];
  error?: EngineErrorCode;
  detail?: string;
}

export type Format = 'woff2' | 'woff' | 'ttf' | 'otf' | 'eot';

export interface ConvertOptions {
  formats: Format[];
  variable: 'keep' | 'static';
  instances?: NamedInstance[] | null;
  subset: 'full' | 'latin' | 'latinExt' | 'custom';
  customText?: string;
  stem?: string;
}

export interface OutputFile {
  name: string;
  format: Format;
  size: number;
  data: Uint8Array;
  family: string;
  styleName: string;
  weight: string;
  stretch: string;
  fontStyle: string;
  variable: boolean;
  stem: string;
}

export interface ConvertResult {
  outputs?: OutputFile[];
  warnings?: { code: 'otfVariable' | 'eotStatic' | 'mergeLayoutStatic'; file: string }[];
  error?: EngineErrorCode;
  detail?: string;
}

/** Fusion de polices statiques en police variable : vérification, puis police construite (build). */
export interface MergeResult {
  ok?: boolean;
  family?: string;
  italic?: boolean;
  axes?: { tag: 'wght' | 'wdth'; min: number; default: number; max: number }[];
  masters?: { file: string; style: string; weight: number; width: number }[];
  stem?: string;
  font?: Uint8Array;
  size?: number;
  warnings?: { code: 'mergeLayoutStatic'; file: string }[];
  error?: MergeErrorCode;
  /** mergeIncompatible / mergeGlyphSet : nombre de glyphes en cause et caractères visibles concernés. */
  count?: number;
  total?: number;
  chars?: string;
  /** mergeSameStyle : graisse en double et fichiers concernés. */
  weight?: string;
  files?: string[];
  detail?: string;
}
