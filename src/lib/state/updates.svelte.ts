// Mises à jour automatiques. Rien n'apparaît tant qu'aucune adresse n'est configurée
// (plugins.updater.endpoints) : pas de vérification, pas de bandeau, pas de ligne dans les Réglages.
import { checkUpdate, installUpdate, updatesEnabled } from '../platform';

type Status = 'idle' | 'checking' | 'upToDate' | 'installing' | 'error' | 'installError';

class Updates {
  enabled = $state(false);
  available = $state<string | null>(null);
  status = $state<Status>('idle');
  dismissed = $state(false);

  /** auto : vérification silencieuse à l’ouverture de la fenêtre. */
  async init(auto: boolean) {
    try {
      this.enabled = await updatesEnabled();
    } catch {
      this.enabled = false;
    }
    if (this.enabled && auto) await this.check(true);
  }

  async check(silent = false) {
    if (!this.enabled || this.status === 'checking' || this.status === 'installing') return;
    this.status = 'checking';
    try {
      this.available = await checkUpdate();
      this.status = this.available || silent ? 'idle' : 'upToDate';
    } catch {
      this.status = silent ? 'idle' : 'error';
    }
  }

  async install() {
    if (!this.available || this.status === 'installing') return;
    this.status = 'installing';
    try {
      await installUpdate(); // l'application redémarre si tout s'est bien passé
    } catch {
      this.status = 'installError';
    }
  }
}

export const updates = new Updates();
