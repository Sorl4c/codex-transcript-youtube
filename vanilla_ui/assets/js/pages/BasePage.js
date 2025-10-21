export class BasePage {
  constructor({ state, services }) {
    this.state = state;
    this.services = services;
    this.container = null;
    this.cleanups = [];
  }

  mount(container) {
    this.container = container;
    this.render(container);
  }

  render() {
    throw new Error("render debe implementarse en la subclase");
  }

  registerCleanup(fn) {
    if (typeof fn === "function") {
      this.cleanups.push(fn);
    }
  }

  unmount() {
    this.cleanups.forEach((dispose) => dispose());
    this.cleanups = [];
    if (this.container) {
      this.container.replaceChildren();
      this.container = null;
    }
  }
}
