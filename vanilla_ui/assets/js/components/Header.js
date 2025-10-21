import { createElement } from "../utils/dom.js";

export class Header {
  constructor({ onToggleTheme }) {
    this.onToggleTheme = onToggleTheme;
    this.element = null;
  }

  render() {
    if (this.element) {
      return this.element;
    }

    const container = createElement("div", {
      classes: "app-header__inner",
    });

    const brand = createElement("div", {
      classes: "brand",
    });

    const title = createElement("span", {
      classes: "brand__title",
      text: "YT Knowledge Hub",
    });

    const subtitle = createElement("span", {
      classes: "brand__subtitle",
      text: "Videoteca RAG",
    });

    brand.append(title, subtitle);

    const actions = createElement("div", {
      classes: "header-actions",
    });

    const themeButton = createElement("button", {
      classes: "header-actions__button",
      attrs: {
        type: "button",
        "aria-label": "Cambiar tema",
      },
      html: `
        <span class="header-actions__icon" aria-hidden="true">🌗</span>
        Tema
      `,
    });

    themeButton.addEventListener("click", () => {
      this.onToggleTheme?.();
    });

    actions.appendChild(themeButton);
    container.append(brand, actions);
    this.element = container;
    return container;
  }
}
