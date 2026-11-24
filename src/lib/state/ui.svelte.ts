// Navigation de la fenêtre principale et état du glisser-déposer.
export type Route = 'conversion' | 'google' | 'variables' | 'results';

class Ui {
  route = $state<Route>('conversion');
  dragging = $state(false);
  dragCount = $state(1);
  go(r: Route) {
    this.route = r;
  }
}

export const ui = new Ui();
