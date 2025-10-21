import { createElement } from "../utils/dom.js";

const NAV_ITEMS = [
  { id: "library", label: "Videoteca", icon: "📚" },
  { id: "ingestion", label: "Ingesta", icon: "⬇️", disabled: true },
  { id: "analysis", label: "Análisis", icon: "📈", disabled: true },
];

export class Sidebar {
  constructor({ onNavigate }) {
    this.onNavigate = onNavigate;
    this.element = null;
    this.activeRoute = "library";
    this.linkElements = new Map();
  }

  render() {
    if (this.element) {
      return this.element;
    }

    const container = document.createDocumentFragment();

    const title = createElement("div", {
      classes: "nav-section__title",
      text: "Navegación",
    });

    const list = createElement("div", {
      classes: "nav-list",
    });

    NAV_ITEMS.forEach((item) => {
      const button = createElement("button", {
        classes: "nav-list__item",
        dataset: {
          active: item.id === this.activeRoute,
        },
        attrs: {
          type: "button",
          "data-route": item.id,
          ...(item.disabled && { disabled: true }),
        },
      });

      button.innerHTML = `<span aria-hidden="true">${item.icon}</span> ${item.label}`;
      if (!item.disabled) {
        button.addEventListener("click", () => {
          this.setActive(item.id);
          this.onNavigate?.(item.id);
        });
      }

      list.appendChild(button);
      this.linkElements.set(item.id, button);
    });

    const wrapper = createElement("div", {
      classes: "nav-section",
    });

    wrapper.append(title, list);
    container.append(wrapper);

    const div = createElement("div");
    div.append(container);
    this.element = div;
    window.addEventListener("hashchange", () => {
      const route = window.location.hash.replace("#", "") || "library";
      this.setActive(route);
    });
    return this.element;
  }

  setActive(route) {
    this.activeRoute = route;
    this.linkElements.forEach((element, id) => {
      element.dataset.active = id === route ? "true" : "false";
    });
  }
}
