export class Router {
  constructor() {
    this.routes = new Map();
    this.currentRoute = null;
    window.addEventListener("popstate", (event) => {
      const route = event.state?.route ?? "library";
      this.navigate(route, { push: false });
    });
  }

  register(routeName, handler) {
    this.routes.set(routeName, handler);
  }

  navigate(routeName, options = {}) {
    if (!this.routes.has(routeName)) {
      console.warn(`Ruta no registrada: ${routeName}`);
      return;
    }

    if (this.currentRoute === routeName && options.force !== true) {
      this.routes.get(routeName)?.();
      return;
    }

    this.currentRoute = routeName;
    if (options.push !== false) {
      window.history.pushState({ route: routeName }, "", `#${routeName}`);
    }
    this.routes.get(routeName)?.();
  }
}
