import { STATE_EVENTS } from "../core/state.js";
import { createElement, clearChildren } from "../utils/dom.js";
import { formatDate, formatDuration } from "../utils/formatters.js";

const DEFAULT_TAB = "summary";

export class VideoDetails {
  constructor({ state, services }) {
    this.state = state;
    this.services = services;
    this.element = null;
    this.contentArea = null;
    this.metaArea = null;
    this.switcherButtons = new Map();
    this.activeTab = DEFAULT_TAB;
    this.currentVideo = null;
    this.unsubscribeSelection = null;
    this.statusMessage = null;
  }

  render() {
    if (this.element) {
      return this.element;
    }

    const container = createElement("section", {
      classes: "video-details",
    });

    const header = createElement("div", {
      classes: "video-details__header",
    });

    const title = createElement("h2", {
      classes: "video-details__title",
    });

    this.metaArea = createElement("div", {
      classes: "video-details__meta",
    });

    const actions = createElement("div", {
      classes: "video-details__actions",
    });

    const copySummary = this.createActionButton({
      label: "Copiar resumen",
      variant: "primary",
      handler: () => this.copyToClipboard(this.currentVideo?.summary, "Resumen copiado"),
    });

    const copyTranscript = this.createActionButton({
      label: "Copiar transcripción",
      handler: () => this.copyToClipboard(this.currentVideo?.transcript, "Transcripción copiada"),
    });

    const deleteVideo = this.createActionButton({
      label: "Eliminar",
      variant: "danger",
      handler: () => this.handleDelete(),
    });

    this.actionButtons = {
      summary: copySummary,
      transcript: copyTranscript,
      delete: deleteVideo,
    };

    actions.append(copySummary, copyTranscript, deleteVideo);

    header.append(title, this.metaArea, actions);

    const content = createElement("div", {
      classes: "video-details__content",
    });

    const switcher = createElement("div", {
      classes: "content-switcher",
    });

    ["summary", "transcript"].forEach((key) => {
      const button = createElement("button", {
        classes: "content-switcher__button",
        attrs: { type: "button" },
        dataset: { active: key === this.activeTab ? "true" : "false" },
        text: key === "summary" ? "Resumen" : "Transcripción",
      });
      button.addEventListener("click", () => this.setActiveTab(key));
      this.switcherButtons.set(key, button);
      switcher.appendChild(button);
    });

    this.contentArea = createElement("div", {
      classes: "video-details__text",
    });

    this.statusMessage = createElement("div", {
      classes: "video-details__status visually-muted",
    });
    this.statusMessage.hidden = true;

    content.append(switcher, this.contentArea, this.statusMessage);

    const footer = createElement("div", {
      classes: "video-details__footer",
    });
    footer.innerHTML = `<small class="visually-muted">Las acciones se aplican sobre la base de datos local.</small>`;

    container.append(header, content, footer);
    this.element = container;

    this.unsubscribeSelection = this.state.subscribe(
      STATE_EVENTS.SELECTION_CHANGED,
      (video) => {
        this.updateDetails(video);
      },
    );

    this.updateDetails(this.state.getSelectedVideo());
    return this.element;
  }

  createActionButton({ label, handler, variant }) {
    const classNames = ["video-details__button"];
    if (variant === "primary") {
      classNames.push("video-details__button--primary");
    } else if (variant === "danger") {
      classNames.push("video-details__button--danger");
    } else {
      classNames.push("video-details__button--ghost");
    }

    const button = createElement("button", {
      classes: classNames.join(" "),
      attrs: { type: "button" },
      text: label,
    });
    button.addEventListener("click", handler);
    return button;
  }

  updateDetails(video) {
    this.currentVideo = video;
    const title = this.element.querySelector(".video-details__title");
    if (!video) {
      title.textContent = "Selecciona un video";
      this.metaArea.innerHTML = "";
      this.renderPlaceholder();
      this.updateActionStates();
      return;
    }

    title.textContent = video.title;
    this.metaArea.innerHTML = `
      <span>📺 ${video.channel}</span>
      <span>🗓 ${formatDate(video.published_at)}</span>
      <span>⏱ ${formatDuration(video.duration)}</span>
      <span class="chip">${video.tags?.[0] ?? "General"}</span>
    `;
    this.renderActiveTab();
    this.updateActionStates();
  }

  renderPlaceholder() {
    clearChildren(this.contentArea);
    this.contentArea.classList.add("placeholder");
    this.contentArea.innerHTML = `
      <strong>Aún no has seleccionado un video</strong>
      <span class="visually-muted">Haz clic en una fila de la tabla para visualizar sus detalles.</span>
    `;
  }

  renderActiveTab() {
    if (!this.currentVideo) {
      this.renderPlaceholder();
      return;
    }
    this.contentArea.classList.remove("placeholder");
    const text =
      this.activeTab === "summary"
        ? this.currentVideo.summary || "Este video todavía no tiene un resumen disponible."
        : this.currentVideo.transcript || "Transcripción pendiente de ingestión.";
    this.contentArea.textContent = text;
    this.switcherButtons.forEach((button, key) => {
      button.dataset.active = key === this.activeTab ? "true" : "false";
    });
  }

  setActiveTab(tab) {
    this.activeTab = tab;
    this.renderActiveTab();
  }

  async copyToClipboard(content, successMessage) {
    if (!content) {
      this.showStatus("No hay contenido para copiar.", true);
      return;
    }
    try {
      if (navigator?.clipboard?.writeText) {
        await navigator.clipboard.writeText(content);
      } else {
        const textarea = document.createElement("textarea");
        textarea.value = content;
        textarea.setAttribute("readonly", "");
        textarea.style.position = "absolute";
        textarea.style.left = "-9999px";
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand("copy");
        document.body.removeChild(textarea);
      }
      this.showStatus(successMessage, false);
    } catch (error) {
      console.error("No se pudo copiar al portapapeles", error);
      this.showStatus("Error al copiar el contenido.", true);
    }
  }

  async handleDelete() {
    if (!this.currentVideo) {
      return;
    }
    if (!window.confirm("¿Seguro que deseas eliminar este video?")) {
      return;
    }
    try {
      await this.services.database.deleteVideo(this.currentVideo.id);
      this.state.deleteVideo(this.currentVideo.id);
      this.showStatus("Video eliminado.", false);
    } catch (error) {
      console.error(error);
      this.showStatus("No se pudo eliminar el video.", true);
    }
  }

  updateActionStates() {
    const hasVideo = Boolean(this.currentVideo);
    if (!this.actionButtons) {
      return;
    }
    this.actionButtons.summary.disabled = !hasVideo || !this.currentVideo.summary;
    this.actionButtons.transcript.disabled =
      !hasVideo || !this.currentVideo.transcript;
    this.actionButtons.delete.disabled = !hasVideo;
  }

  showStatus(message, isError = false) {
    if (!this.statusMessage) {
      return;
    }
    this.statusMessage.hidden = false;
    this.statusMessage.textContent = message;
    this.statusMessage.style.color = isError
      ? "var(--color-danger)"
      : "var(--color-text-muted)";
    window.clearTimeout(this.statusTimeout);
    this.statusTimeout = window.setTimeout(() => {
      this.statusMessage.hidden = true;
    }, 2800);
  }

  destroy() {
    this.unsubscribeSelection?.();
    window.clearTimeout(this.statusTimeout);
  }
}
