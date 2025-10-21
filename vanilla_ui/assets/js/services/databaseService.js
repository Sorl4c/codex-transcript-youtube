import { Video } from "../models/video.js";

export class DatabaseService {
  constructor(sourcePath) {
    this.sourcePath = sourcePath;
    this.cache = null;
  }

  async load() {
    if (this.cache) {
      return this.cache;
    }

    const response = await fetch(this.sourcePath, {
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`No se pudieron obtener los datos: ${response.status}`);
    }

    const payload = await response.json();
    this.cache = Array.isArray(payload) ? payload.map(Video.fromJson) : [];
    return this.cache;
  }

  async getAllVideos() {
    const videos = await this.load();
    return videos.map((video) => ({ ...video }));
  }

  async getVideoById(id) {
    const videos = await this.load();
    const match = videos.find((video) => video.id === id);
    return match ? { ...match } : null;
  }

  async deleteVideo(id) {
    const videos = await this.load();
    const index = videos.findIndex((video) => video.id === id);
    if (index === -1) {
      throw new Error("No se encontró el video solicitado.");
    }
    const [removed] = videos.splice(index, 1);
    return { ...removed };
  }

  async updateSummary(id, summary) {
    const videos = await this.load();
    const video = videos.find((item) => item.id === id);
    if (!video) {
      throw new Error("No se encontró el video solicitado.");
    }
    video.summary = summary;
    return { ...video };
  }
}
