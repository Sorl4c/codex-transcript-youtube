import { STATE_EVENTS } from "../core/state.js";
import { createElement, clearChildren } from "../utils/dom.js";
import { formatDate, truncateText } from "../utils/formatters.js";

const SORTABLE_COLUMNS = [
  { field: "title", label: "Título" },
  { field: "channel", label: "Canal" },
  { field: "published_at", label: "Fecha" },
];

export class VideoTable {
  constructor({ state }) {
    this.state = state;
    this.element = null;
    this.tbody = null;
    this.emptyState = null;
    this.paginationElement = null;
    this.unsubscribeCollection = null;
    this.unsubscribeSelection = null;
    this.currentSelection = null;
    this.sortButtons = new Map();
    this.countBadge = null;
  }

  render() {
    if (this.element) {
      return this.element;
    }

    this.currentSelection = this.state.getSelectedVideo()?.id ?? null;

    const container = createElement("section", {
      classes: "video-table",
    });

    const header = createElement("div", {
      classes: "video-table__header",
    });

    const headerLeft = createElement("div", {
      classes: "video-table__header-left",
    });

    const title = createElement("h2", {
      classes: "video-table__title",
      text: "Listado de videos",
    });

    headerLeft.append(title);

    const headerRight = createElement("div", {
      classes: "video-table__header-right",
    });

    this.countBadge = createElement("span", {
      classes: "video-table__counter chip",
    });

    headerRight.append(this.countBadge);

    header.append(headerLeft, headerRight);

    const tableWrapper = createElement("div", {
      classes: "table-responsive",
    });

    const table = createElement("table", {
      classes: "table",
    });

    const thead = this.buildHeader();
    this.tbody = createElement("tbody");

    table.append(thead, this.tbody);
    tableWrapper.appendChild(table);

    this.emptyState = createElement("div", {
      classes: "empty-state",
      text: "No se encontraron videos para los criterios seleccionados.",
    });
    this.emptyState.hidden = true;

    this.paginationElement = this.createPagination();

    container.append(header, tableWrapper, this.emptyState, this.paginationElement);
    this.element = container;

    this.unsubscribeCollection = this.state.subscribe(
      STATE_EVENTS.COLLECTION_UPDATED,
      (videos) => {
        this.updateTable(videos);
        this.updateSortIndicators();
        this.updatePagination();
        this.updateCounter();
      },
    );

    this.unsubscribeSelection = this.state.subscribe(
      STATE_EVENTS.SELECTION_CHANGED,
      (video) => {
        this.currentSelection = video?.id ?? null;
        this.highlightSelection();
      },
    );

    this.updateTable(this.state.getVisibleVideos());
    this.updateSortIndicators();
    this.updatePagination();
    this.updateCounter();
    return this.element;
  }

  buildHeader() {
    const thead = createElement("thead");
    const row = createElement("tr");

    SORTABLE_COLUMNS.forEach((column) => {
      const th = createElement("th");
      const button = createElement("button", { text: column.label, attrs: { type: "button" } });
      button.setAttribute("aria-label", `Ordenar por ${column.label}`);
      button.addEventListener("click", () => {
        this.state.setSort(column.field);
        this.updateSortIndicators();
      });
      th.setAttribute("role", "columnheader");
      th.setAttribute("aria-sort", "none");
      th.appendChild(button);
      row.appendChild(th);
      this.sortButtons.set(column.field, { button, label: column.label, header: th });
    });

    const transcriptHeader = createElement("th", { text: "Transcripción" });
    row.appendChild(transcriptHeader);

    thead.appendChild(row);
    return thead;
  }

  updateSortIndicators() {
    const { field, direction } = this.state.sort;
    this.sortButtons.forEach(({ button, label, header }, column) => {
      if (column === field) {
        button.innerHTML = `${label} <span aria-hidden="true">${direction === "asc" ? "▲" : "▼"}</span>`;
        header.setAttribute("aria-sort", direction === "asc" ? "ascending" : "descending");
      } else {
        button.textContent = label;
        header.setAttribute("aria-sort", "none");
      }
    });
  }

  createPagination() {
    const container = createElement("div", {
      classes: "pagination",
    });

    const metaInfo = createElement("span");
    metaInfo.className = "pagination__meta";

    const controls = createElement("div", {
      classes: "pagination__controls",
    });

    const prev = createElement("button", {
      text: "Anterior",
      attrs: { type: "button" },
    });
    const next = createElement("button", {
      text: "Siguiente",
      attrs: { type: "button" },
    });

    prev.addEventListener("click", () => {
      const { currentPage } = this.state.getPaginationMeta();
      if (currentPage > 1) {
        this.state.setPage(currentPage - 1);
      }
    });

    next.addEventListener("click", () => {
      const { currentPage, totalPages } = this.state.getPaginationMeta();
      if (currentPage < totalPages) {
        this.state.setPage(currentPage + 1);
      }
    });

    controls.append(prev, next);
    container.append(metaInfo, controls);
    container.metaInfo = metaInfo;
    container.prev = prev;
    container.next = next;
    return container;
  }

  updateTable(videos) {
    if (!this.tbody) {
      return;
    }
    clearChildren(this.tbody);
    if (!videos || videos.length === 0) {
      this.tbody.hidden = true;
      this.emptyState.hidden = false;
      return;
    }

    this.tbody.hidden = false;
    this.emptyState.hidden = true;

    videos.forEach((video) => {
      const row = this.buildRow(video);
      this.tbody.appendChild(row);
    });

    this.highlightSelection();
  }

  buildRow(video) {
    const row = createElement("tr", {
      dataset: {
        id: video.id,
        active: video.id === this.currentSelection ? "true" : "false",
      },
    });

    const titleCell = createElement("td", {
      html: `
        <strong>${video.title}</strong>
        <small>${truncateText(video.summary, 90) || "Sin resumen disponible"}</small>
      `,
    });

    const channelCell = createElement("td", {
      html: `
        <span class="table__channel">
          ${video.channel}
        </span>
      `,
    });

    const dateCell = createElement("td", {
      classes: "table__date",
      text: formatDate(video.published_at),
    });

    const transcriptCell = createElement("td", {
      text: video.transcript ? "Disponible" : "Pendiente",
    });

    row.append(titleCell, channelCell, dateCell, transcriptCell);

    row.addEventListener("click", () => {
      this.state.selectVideo(video.id);
    });

    return row;
  }

  updatePagination() {
    if (!this.paginationElement) {
      return;
    }
    const meta = this.state.getPaginationMeta();
    this.paginationElement.metaInfo.textContent = meta.totalItems
      ? `Mostrando ${meta.start} - ${meta.end} de ${meta.totalItems}`
      : "Sin resultados que mostrar";

    this.paginationElement.prev.disabled = meta.currentPage <= 1;
    this.paginationElement.next.disabled = meta.currentPage >= meta.totalPages;
  }

  updateCounter() {
    if (!this.countBadge) {
      return;
    }
    const meta = this.state.getPaginationMeta();
    this.countBadge.textContent = meta.totalItems
      ? `${meta.totalItems} ${meta.totalItems === 1 ? "video" : "videos"}`
      : "Sin resultados";
  }

  highlightSelection() {
    if (!this.tbody) {
      return;
    }
    this.tbody.querySelectorAll("tr").forEach((row) => {
      row.dataset.active = row.dataset.id === this.currentSelection ? "true" : "false";
    });
  }

  destroy() {
    this.unsubscribeCollection?.();
    this.unsubscribeSelection?.();
  }
}
