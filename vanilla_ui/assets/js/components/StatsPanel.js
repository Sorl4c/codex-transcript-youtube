import { STATE_EVENTS } from "../core/state.js";
import { createElement } from "../utils/dom.js";

export class StatsPanel {
  constructor({ state }) {
    this.state = state;
    this.element = null;
    this.unsubscribe = null;
  }

  render() {
    if (this.element) {
      return this.element;
    }

    const container = createElement("div", {
      classes: "stats-panel",
    });

    this.element = container;
    this.updateCards(this.state.getStats());

    this.unsubscribe = this.state.subscribe(STATE_EVENTS.STATS_UPDATED, (stats) =>
      this.updateCards(stats),
    );

    return this.element;
  }

  updateCards(stats) {
    if (!this.element) {
      return;
    }
    this.element.innerHTML = `
      ${this.cardTemplate("Total videos", stats.total)}
      ${this.cardTemplate("Con resumen", stats.withSummary, {
        meta: this.percentage(stats.withSummary, stats.total),
      })}
      ${this.cardTemplate("Con transcripción", stats.withTranscript, {
        meta: this.percentage(stats.withTranscript, stats.total),
      })}
    `;
  }

  percentage(part, total) {
    if (!total) {
      return "0 %";
    }
    return `${Math.round((part / total) * 100)} %`;
  }

  cardTemplate(label, value, options = {}) {
    return `
      <article class="stats-card">
        <span class="stats-card__label">${label}</span>
        <span class="stats-card__value">${value}</span>
        ${
          options.meta
            ? `<span class="stats-card__meta">Equivale a ${options.meta}</span>`
            : ""
        }
      </article>
    `;
  }

  destroy() {
    this.unsubscribe?.();
  }
}
