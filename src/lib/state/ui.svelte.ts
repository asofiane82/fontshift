// Navigation de la fenêtre principale et état du glisser-déposer.
export type Route = 'conversion' | 'google' | 'variables' | 'results';

class Ui {
  route = $state<Route>('conversion');
  dragging = $state(false);
  dragCount = $state(1);
  /** Écran à rouvrir après un téléchargement Google Fonts (l'Aperçu avancé quand on vient de lui). */
  returnTo = $state<Route | null>(null);
  go(r: Route, returnTo: Route | null = null) {
    this.route = r;
    this.returnTo = returnTo;
  }
}

export const ui = new Ui();
