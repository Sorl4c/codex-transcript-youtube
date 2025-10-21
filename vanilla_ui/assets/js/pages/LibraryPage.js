import { BasePage } from "./BasePage.js";
import { createElement } from "../utils/dom.js";
import { SearchBar } from "../components/SearchBar.js";
import { VideoTable } from "../components/VideoTable.js";
import { VideoDetails } from "../components/VideoDetails.js";
import { StatsPanel } from "../components/StatsPanel.js";

export class LibraryPage extends BasePage {
  render(container) {
    container.classList.add("library-page");

    const header = createElement("div", {
      classes: "library-page__header",
    });

    const heading = createElement("div", {
      classes: "library-page__heading",
    });

    const title = createElement("h1", {
      classes: "library-page__title",
      text: "Videoteca",
    });

    const subtitle = createElement("p", {
      classes: "library-page__subtitle",
      text: "Gestiona tus transcripciones y resúmenes con búsqueda instantánea.",
    });

    heading.append(title, subtitle);

    const searchBar = new SearchBar({ state: this.state });
    const searchElement = searchBar.render();

    const statsPanel = new StatsPanel({ state: this.state });

    header.append(heading, searchElement);

    const statsElement = statsPanel.render();

    const content = createElement("div", {
      classes: "library-page__content",
    });

    const tableWrapper = createElement("div", {
      classes: "library-page__table",
    });
    const detailsWrapper = createElement("div", {
      classes: "library-page__details",
    });

    const videoTable = new VideoTable({ state: this.state });
    const tableElement = videoTable.render();

    const videoDetails = new VideoDetails({
      state: this.state,
      services: this.services,
    });
    const detailsElement = videoDetails.render();

    tableWrapper.appendChild(tableElement);
    detailsWrapper.appendChild(detailsElement);
    content.append(tableWrapper, detailsWrapper);

    container.append(header, statsElement, content);

    this.registerCleanup(() => searchBar.destroy());
    this.registerCleanup(() => videoTable.destroy());
    this.registerCleanup(() => videoDetails.destroy());
    this.registerCleanup(() => statsPanel.destroy());
  }
}
