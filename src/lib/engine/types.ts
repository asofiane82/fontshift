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
  warnings?: { code: 'otfVariable' | 'eotStatic'; file: string }[];
  error?: EngineErrorCode;
  detail?: string;
}
