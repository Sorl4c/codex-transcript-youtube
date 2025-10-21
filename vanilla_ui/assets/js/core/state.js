const EVENTS = {
  COLLECTION_UPDATED: "collection:updated",
  SELECTION_CHANGED: "selection:changed",
  SEARCH_CHANGED: "search:changed",
  ERROR: "error",
  STATS_UPDATED: "stats:updated",
};

export class State {
  constructor() {
    this.videos = [];
    this.videoMap = new Map();
    this.filteredIds = [];
    this.sort = { field: "published_at", direction: "desc" };
    this.pagination = { pageSize: 10, currentPage: 1 };
    this.searchTerm = "";
    this.selectedVideoId = null;
    this.error = null;
    this.listeners = new Map();
  }

  subscribe(event, handler) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event).add(handler);
    return () => {
      this.listeners.get(event)?.delete(handler);
    };
  }

  emit(event, payload) {
    this.listeners.get(event)?.forEach((handler) => handler(payload));
  }

  setVideos(videos) {
    this.videos = Array.isArray(videos) ? [...videos] : [];
    this.videoMap = new Map(this.videos.map((video) => [video.id, video]));
    this.pagination.currentPage = 1;
    this.applyFilters();
    this.emit(EVENTS.STATS_UPDATED, this.getStats());
  }

  setError(message) {
    this.error = message;
    this.emit(EVENTS.ERROR, message);
  }

  clearError() {
    this.error = null;
    this.emit(EVENTS.ERROR, null);
  }

  getStats() {
    const total = this.videos.length;
    const withSummary = this.videos.filter(
      (video) => (video.summary ?? "").trim().length > 0,
    ).length;
    const withTranscript = this.videos.filter(
      (video) => (video.transcript ?? "").trim().length > 0,
    ).length;

    return {
      total,
      withSummary,
      withTranscript,
    };
  }

  applyFilters() {
    const query = this.searchTerm.trim().toLowerCase();
    const filtered = query
      ? this.videos.filter((video) => {
          const haystack = [
            video.title,
            video.channel,
            video.summary,
            ...(video.tags ?? []),
          ]
            .filter(Boolean)
            .join(" ")
            .toLowerCase();
          return haystack.includes(query);
        })
      : [...this.videos];

    const sorted = this.sortCollection(filtered);
    this.filteredIds = sorted.map((video) => video.id);
    this.ensureValidPage();
    this.emit(EVENTS.COLLECTION_UPDATED, this.getVisibleVideos());
  }

  sortCollection(collection) {
    const { field, direction } = this.sort;
    const modifier = direction === "desc" ? -1 : 1;
    return [...collection].sort((a, b) => {
      if (field === "published_at") {
        const dateA = new Date(a.published_at ?? 0).getTime();
        const dateB = new Date(b.published_at ?? 0).getTime();
        return dateA > dateB ? -modifier : dateA < dateB ? modifier : 0;
      }

      const valueA = (a[field] ?? "").toString().toLowerCase();
      const valueB = (b[field] ?? "").toString().toLowerCase();
      return valueA > valueB ? modifier : valueA < valueB ? -modifier : 0;
    });
  }

  getVisibleVideos() {
    const { pageSize, currentPage } = this.pagination;
    const start = (currentPage - 1) * pageSize;
    const end = start + pageSize;
    const ids = this.filteredIds.slice(start, end);
    return ids.map((id) => this.videoMap.get(id)).filter(Boolean);
  }

  getPaginationMeta() {
    const { pageSize, currentPage } = this.pagination;
    const totalItems = this.filteredIds.length;
    const totalPages = Math.max(Math.ceil(totalItems / pageSize), 1);
    const start = totalItems === 0 ? 0 : (currentPage - 1) * pageSize + 1;
    const end = Math.min(currentPage * pageSize, totalItems);
    return {
      pageSize,
      currentPage,
      totalItems,
      totalPages,
      start,
      end,
    };
  }

  ensureValidPage() {
    const { currentPage, pageSize } = this.pagination;
    const totalPages = Math.max(
      Math.ceil(this.filteredIds.length / pageSize),
      1,
    );
    if (currentPage > totalPages) {
      this.pagination.currentPage = totalPages;
    }
    if (this.pagination.currentPage < 1) {
      this.pagination.currentPage = 1;
    }
  }

  setSearchTerm(term) {
    this.searchTerm = term;
    this.pagination.currentPage = 1;
    this.emit(EVENTS.SEARCH_CHANGED, term);
    this.applyFilters();
  }

  setSort(field) {
    if (this.sort.field === field) {
      this.sort.direction = this.sort.direction === "asc" ? "desc" : "asc";
    } else {
      this.sort.field = field;
      this.sort.direction = field === "published_at" ? "desc" : "asc";
    }
    this.applyFilters();
  }

  setPage(pageNumber) {
    this.pagination.currentPage = pageNumber;
    this.ensureValidPage();
    this.emit(EVENTS.COLLECTION_UPDATED, this.getVisibleVideos());
  }

  setPageSize(size) {
    this.pagination.pageSize = size;
    this.pagination.currentPage = 1;
    this.applyFilters();
  }

  selectVideo(id) {
    this.selectedVideoId = id;
    this.emit(EVENTS.SELECTION_CHANGED, this.getSelectedVideo());
  }

  getSelectedVideo() {
    return this.selectedVideoId
      ? this.videoMap.get(this.selectedVideoId) ?? null
      : null;
  }

  deleteVideo(id) {
    if (!this.videoMap.has(id)) {
      return;
    }
    this.videoMap.delete(id);
    this.videos = this.videos.filter((video) => video.id !== id);
    this.filteredIds = this.filteredIds.filter((videoId) => videoId !== id);
    if (this.selectedVideoId === id) {
      this.selectedVideoId = null;
      this.emit(EVENTS.SELECTION_CHANGED, null);
    }
    this.ensureValidPage();
    this.emit(EVENTS.COLLECTION_UPDATED, this.getVisibleVideos());
    this.emit(EVENTS.STATS_UPDATED, this.getStats());
  }

  updateVideoSummary(id, summary) {
    const video = this.videoMap.get(id);
    if (!video) {
      return;
    }
    video.summary = summary;
    this.emit(EVENTS.COLLECTION_UPDATED, this.getVisibleVideos());
    if (this.selectedVideoId === id) {
      this.emit(EVENTS.SELECTION_CHANGED, video);
    }
    this.emit(EVENTS.STATS_UPDATED, this.getStats());
  }
}

export { EVENTS as STATE_EVENTS };
