import { STATE_EVENTS } from "../core/state.js";
import { createElement } from "../utils/dom.js";

const DEBOUNCE_MS = 200;

export class SearchBar {
  constructor({ state }) {
    this.state = state;
    this.element = null;
    this.input = null;
    this.clearButton = null;
    this.debounceId = null;
    this.unsubscribe = null;
  }

  render() {
    if (this.element) {
      return this.element;
    }

    const wrapper = createElement("div", {
      classes: "search-bar",
    });

    this.input = createElement("input", {
      classes: "search-bar__input",
      attrs: {
        type: "search",
        placeholder: "Buscar por título, canal o resumen",
        "aria-label": "Buscar videos",
      },
    });

    this.input.value = this.state.searchTerm ?? "";

    this.input.addEventListener("input", (event) => {
      const value = event.target.value;
      window.clearTimeout(this.debounceId);
      this.debounceId = window.setTimeout(() => {
        this.state.setSearchTerm(value);
      }, DEBOUNCE_MS);
      this.toggleClearButton();
    });

    this.clearButton = createElement("button", {
      classes: "search-bar__clear",
      attrs: {
        type: "button",
        "aria-label": "Limpiar búsqueda",
      },
      html: "&times;",
    });

    this.clearButton.addEventListener("click", () => {
      this.input.value = "";
      this.state.setSearchTerm("");
      this.toggleClearButton();
    });

    const icon = createElement("span", {
      classes: "search-bar__icon",
      html: `
        <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
          <path fill="currentColor" d="M10 2a8 8 0 0 1 6.32 12.906l5.387 5.387-1.414 1.414-5.387-5.387A8 8 0 1 1 10 2Zm0 2a6 6 0 1 0 0 12 6 6 0 0 0 0-12Z"/>
        </svg>
      `,
    });

    wrapper.append(this.input, this.clearButton, icon);
    this.element = wrapper;

    this.unsubscribe = this.state.subscribe(STATE_EVENTS.SEARCH_CHANGED, (term) => {
      if (this.input && this.input.value !== term) {
        this.input.value = term;
        this.toggleClearButton();
      }
    });

    this.toggleClearButton();

    return this.element;
  }

  destroy() {
    window.clearTimeout(this.debounceId);
    this.unsubscribe?.();
  }

  toggleClearButton() {
    if (this.clearButton) {
      this.clearButton.hidden = !this.input?.value;
    }
  }
}
