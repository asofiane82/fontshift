// Client du moteur : file d'appels vers le worker, état de démarrage, annulation immédiate.
import type { ConvertOptions, ConvertResult, OpenResult } from './types';

type Pending = { resolve: (v: unknown) => void; reject: (e: Error) => void };

class EngineClient {
  state = $state<'idle' | 'loading' | 'ready' | 'error'>('idle');
  detail = $state('');
  private worker: Worker | null = null;
  private pending = new Map<number, Pending>();
  private seq = 0;

  start() {
    if (this.worker) return;
    this.state = 'loading';
    this.worker = new Worker(new URL('./worker.ts', import.meta.url), { type: 'module' });
    this.worker.onmessage = (e) => {
      const msg = e.data;
      if (msg.type === 'status') {
        this.state = msg.state;
        this.detail = msg.detail ?? '';
        return;
      }
      const p = this.pending.get(msg.id);
      if (!p) return;
      this.pending.delete(msg.id);
      if (msg.ok) p.resolve(msg.result);
      else p.reject(new Error(msg.error));
    };
    this.worker.onerror = (e) => {
      this.state = 'error';
      this.detail = e.message;
    };
  }

  private call<T>(payload: Record<string, unknown>, transfer: Transferable[] = []): Promise<T> {
    this.start();
    const id = ++this.seq;
    return new Promise<T>((resolve, reject) => {
      this.pending.set(id, { resolve: resolve as (v: unknown) => void, reject });
      this.worker!.postMessage({ id, ...payload }, transfer);
    });
  }

  /** Analyse un fichier (une entrée par police d'une collection). */
  open(bytes: Uint8Array, filename: string) {
    return this.call<OpenResult>({ op: 'open', bytes: bytes.slice(), filename });
  }

  convert(bytes: Uint8Array, filename: string, options: ConvertOptions) {
    const copy = bytes.slice();
    return this.call<ConvertResult>({ op: 'convert', bytes: copy, filename, options }, [copy.buffer]);
  }

  /** Arrête net le travail en cours ; le moteur redémarre en arrière-plan. */
  cancel() {
    if (!this.worker) return;
    this.worker.terminate();
    this.worker = null;
    for (const p of this.pending.values()) p.reject(new Error('cancelled'));
    this.pending.clear();
    this.start();
  }
}

export const engine = new EngineClient();
